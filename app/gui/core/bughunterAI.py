from transformers import BertModel, BertTokenizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from bs4 import BeautifulSoup
import torch
import spacy
import requests
import redis
import numpy as np
import aiohttp
from urllib.parse import urljoin
from dataclasses import dataclass
import time
import re
import os
import logging
import json
import copy as cp
import asyncio
import yaml
import faiss

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BugHunterAI")

@dataclass
class GPUPatternMatcher:
    def __init__(self, templates):
        self.patterns = np.array([t["pattern"] for t in templates])

    def match_patterns(self, content):
        content_gpu = np.array(content)
        matches = np.zeros(len(self.patterns), dtype=bool)

        # Custom CUDA kernel for matching each pattern in the content
        import cupy as cp

        match_kernel = cp.RawKernel(r"""
        extern "C" __global__
        void match(const char* content, const char* patterns, const int* pattern_lengths, bool* matches, int num_patterns) {
            int idx = blockIdx.x * blockDim.x + threadIdx.x;
            if (idx < num_patterns) {
                bool found = false;
                for (int i = 0; i < strlen(content) - pattern_lengths[idx] + 1; ++i) {
                    if (memcmp(&content[i], &patterns[idx * pattern_lengths[idx]], pattern_lengths[idx]) == 0) {
                        found = true;
                        break;
                    }
                }
                matches[idx] = found;
            }
        }
        """, 'match')

        content_gpu = cp.array(content)
        patterns_gpu = cp.array(self.patterns.ravel())
        pattern_lengths_gpu = cp.array([len(p) for p in self.patterns])
        matches_gpu = cp.zeros(len(self.patterns), dtype=bool)

        match_kernel((len(self.patterns) // 256 + 1,), (256,), (content_gpu, patterns_gpu, pattern_lengths_gpu, matches_gpu, len(self.patterns)))

        matches = cp.get(matches_gpu)
        return matches

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

# Initialize spaCy for NLP tasks
nlp = spacy.load("en_core_web_sm")

@dataclass
class NucleiKnowledgeBase:
    def __init__(self):
        self.templates = []
        self.vector_db = None
        self.tfidf_vectorizer = TfidfVectorizer()  # noqa: E501  # noqa: E501
        self.tfidf_matrix = None

    def load_templates(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                with open(os.path.join(root, file), encoding="utf-8") as f:
                    template = yaml.safe_load(f)
                    self.templates.append(template)
                with open(os.path.join(root, file), encoding="utf-8") as f:
                    self.templates.append(template)
                with open(os.path.join(root, file), encoding="utf-8") as f:
                    template = yaml.safe_load(f)
                    self.templates.append(template)
    # Create TF-IDF matrix for all templates
    def create_vector_db(self):
        embeddings = []
        for template in self.templates:
            embedding = self.get_embedding(json.dumps(template))
            embeddings.append(embedding)

        dimension = embeddings[0].shape[0]
        self.vector_db = faiss.IndexFlatIP(dimension)
        self.vector_db.add(np.array(embeddings))

    def get_embedding(self, text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    def find_similar_templates(self, query, k=5):
        query_embedding = self.get_embedding(query)
        _, indices = self.vector_db.search(np.array([query_embedding]), k)

        # Use TF-IDF similarity as a secondary ranking
        query_tfidf = self.tfidf_vectorizer.transform([query])
        tfidf_similarities = cosine_similarity(query_tfidf, self.tfidf_matrix[indices[0]])

        # Combine BERT and TF-IDF rankings
        combined_rankings = list(zip(indices[0], tfidf_similarities[0]))
        combined_rankings.sort(key=lambda x: x[1], reverse=True)

        return [self.templates[i] for i, _ in combined_rankings]

@dataclass
class AdaptiveTemplateManager:
    def __init__(self, initial_templates):
        self.templates = initial_templates
        self.performance_metrics = {}

    def update_template_performance(self, template_id, success, false_positive):
        if template_id not in self.performance_metrics:
            self.performance_metrics[template_id] = {
                "successes": 0,
                "false_positives": 0,
            }
        self.performance_metrics[template_id]["successes"] += int(success)
        self.performance_metrics[template_id]["false_positives"] += int(false_positive)

    def optimize_templates(self):
        for template_id, metrics in self.performance_metrics.items():
            if metrics["false_positives"] > metrics["successes"]:
                self.adjust_template(template_id)

    def adjust_template(self, template_id):
        logger.info(f"Adjusting template with ID: {template_id}")

@dataclass
class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_times = []

    async def can_make_request(self):
        current_time = time.time()
        self.request_times = [t for t in self.request_times if current_time - t < self.time_window]
        if len(self.request_times) < self.max_requests:
            self.request_times.append(current_time)
            return True
        return False

    async def wait_for_next_window(self):
        await asyncio.sleep(self.time_window)

class WebsiteScanner:
    """
    WebsiteScanner class for scanning websites for vulnerabilities.
    Attributes:
        knowledge_base (KnowledgeBase): The knowledge base containing vulnerability templates.
        session (requests.Session): The HTTP session for making requests.
        rate_limiter (RateLimiter): The rate limiter to control the request rate.
        cache_client (redis.Redis): The Redis client for caching.
    Methods:
        scan_website(url):
            Scans a website for vulnerabilities.
            Args:
                url (str): The URL of the website to scan.
            Returns:
                list: A list of validated vulnerabilities.
        fetch_website_content(url, session=None):
            Fetches the content and links of a website.
            Args:
                url (str): The URL of the website.
                session (aiohttp.ClientSession, optional): The HTTP session for making requests.
            Returns:
                tuple: A tuple containing the content and links of the website.
        analyze_content(content, url):
            Analyzes the content of a website for vulnerabilities.
            Args:
                content (str): The content of the website.
                url (str): The URL of the website.
            Returns:
                list: A list of vulnerabilities found in the content.
        match_templates(content, templates, url):
            Matches the content of a website against vulnerability templates.
            Args:
                content (str): The content of the website.
                templates (list): A list of vulnerability templates.
                url (str): The URL of the website.
            Returns:
                list: A list of vulnerabilities found in the content.
        apply_template(content, template, url):
            Applies a vulnerability template to the content of a website.
            Args:
                content (str): The content of the website.
                template (dict): A vulnerability template.
                url (str): The URL of the website.
            Returns:
                bool: True if the template matches the content, False otherwise.
        validate_vulnerabilities(vulnerabilities):
            Validates the vulnerabilities found in the content.
            Args:
                vulnerabilities (list): A list of vulnerabilities.
            Returns:
                list: A list of validated vulnerabilities.
        cross_validate_with_cve(vulnerability):
            Cross-validates a vulnerability with the CVE database.
            Args:
                vulnerability (dict): A vulnerability.
            Returns:
                bool: True if the vulnerability is valid, False otherwise.
    """
    def __init__(self, knowledge_base):
        """
        The function initializes an object with a knowledge base and a session with specific headers for
        making HTTP requests.
        
        :param knowledge_base: The `knowledge_base` parameter in the `__init__` method is used to
        initialize an instance of a class with a knowledge base. This knowledge base could be a data
        structure, a database connection, or any other information repository that the class needs to
        operate on or interact with during its lifecycle
        """
        self.knowledge_base = knowledge_base
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"  # noqa: E501
        })
        self.rate_limiter = RateLimiter(max_requests=10, time_window=1)  # 10 requests per second
        self.cache_client = redis.Redis(host="localhost", port=6379, db=0)

    async def scan_website(self, url, session):
        while not await self.rate_limiter.can_make_request():
            await self.rate_limiter.wait_for_next_window()
        content, links = await self.fetch_website_content(url, session)
        vulnerabilities = await self.analyze_content(content, url)

    # Scan additional pages
        tasks = [self.fetch_website_content(link, session) for link in links[:5]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for link, result in zip(links[:5], results):
            if isinstance(result, Exception):
                logger.error(f"Error scanning link: {result}")
            else:
                content, _ = result
                vulnerabilities.extend(await self.analyze_content(content, link))
        return await self.validate_vulnerabilities(vulnerabilities)

    async def fetch_website_content(self, url, session=None):
        async with session.get(url) as response:
            content = await response.text()
        soup = BeautifulSoup(content, "html.parser")
        links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]
        return content, links

    async def analyze_content(self, content, url):
        soup = BeautifulSoup(content, "html.parser")
        text_content = soup.get_text()

        doc = nlp(text_content)
        key_phrases = [chunk.text for chunk in doc.noun_chunks]

        relevant_templates = []
        for phrase in key_phrases:
            relevant_templates.extend(self.knowledge_base.find_similar_templates(phrase))

        return await self.match_templates(content, relevant_templates, url)

    async def match_templates(self, content, templates, url):
        vulnerabilities = []
        for template in templates:
            if await self.apply_template(content, template, url):
                vulnerability = {
                    "name": template.get("name", "Unknown"),
                    "severity": template.get("info", {}).get("severity", "Unknown"),
                    "description": template.get("info", {}).get("description", "No description"),
                    "url": url,
                    "template": template,
                }
                vulnerabilities.append(vulnerability)
        return vulnerabilities

    async def apply_template(self, content, template, url):
        matchers = template.get("matchers", [])
        for matcher in matchers:
            if matcher["type"] == "word":
                if all(word in content for word in matcher["words"]):
                    return True
            elif matcher["type"] == "regex":
                if re.search(matcher["regex"], content):
                    return True
            elif matcher["type"] == "status":
                response = await self.session.get(url)
                if response.status_code == matcher["status"]:
                    return True
        return False

    async def validate_vulnerabilities(self, vulnerabilities):
        validated_vulnerabilities = []
        for vuln in vulnerabilities:
            # Implement additional validation logic here
            if await self.cross_validate_with_cve(vuln):
                validated_vulnerabilities.append(vuln)
        return validated_vulnerabilities

    async def cross_validate_with_cve(self, vulnerability):
        # Implement CVE cross-validation logic
        return True

@dataclass
class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_times = []

    async def can_make_request(self):
        current_time = time.time()
        self.request_times = [t for t in self.request_times if current_time - t < self.time_window]
        if len(self.request_times) < self.max_requests:
            self.request_times.append(current_time)
            return True
        return False

    async def wait_for_next_window(self):
        await asyncio.sleep(self.time_window)

async def main():
    kb = NucleiKnowledgeBase()
    kb.load_templates("/path/to/nuclei-templates")
    kb.create_vector_db()

    scanner = WebsiteScanner(kb)

    url = input("Enter the URL to scan: ")
    url = input("Enter the URL to scan: ")
    async with aiohttp.ClientSession() as session:
        vulnerabilities = await scanner.scan_website(url, session)
    if vulnerabilities:
        print("Vulnerabilities found:")
        for vuln in vulnerabilities:
            print(f"- {vuln['name']} (Severity: {vuln['severity']})")
            print(f"  URL: {vuln['url']}")
            print(f"  Description: {vuln['description']}")
    else:
        print("No vulnerabilities detected.")

if __name__ == "__main__":
    asyncio.run(main())
