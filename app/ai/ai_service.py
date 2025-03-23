import os
import json
from datetime import datetime
import logging
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import openai
import aiohttp
from bs4 import BeautifulSoup
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.initialized = False
        self.config = {}
        self.models = {}
        self.api_type = "openai"
        self.openai_client = None
        self.codegpt_api_key = None
        self.cache_dir = Path("cache")
        self.technology_patterns = {
            "wordpress": [r"wp-content", r"wp-includes", r"wordpress"],
            "php": [r"\.php", r"PHP_SESSION_ID"],
            "java": [r"\.jsp", r"\.do", r"j_session_id"],
            "python": [r"\.py", r"django", r"flask"],
            "node.js": [r"node_modules", r"express", r"next.js"],
            "database": [r"mysql", r"postgresql", r"mongodb"],
        }

    def initialize(self) -> bool:
        """Initialize AI service with configuration"""
        try:
            self._load_config()
            self._set_api_type()
            self._initialize_api_client()
            self._load_models()
            self.initialized = True
            logger.info(
                f"AI service initialized successfully using {self.api_type} API"
            )
            return True
        except (json.JSONDecodeError, ValueError, OSError) as e:
            logger.error(f"AI service initialization failed: {str(e)}")
            return False

    def _load_config(self):
        config_file = Path("config/ai_config.json")
        if config_file.exists():
            with open(config_file, "r") as f:
                self.config = json.load(f)

    def _set_api_type(self):
        self.api_type = self.config.get("ai_api_type", "openai")

    def _initialize_api_client(self):
        if self.api_type == "openai":
            if not (
                openai_api_key := self.config.get("openai_api_key")
                or os.getenv("OPENAI_API_KEY")
            ):
                raise ValueError("OpenAI API key not configured")
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
        elif self.api_type == "codegpt":
            self.codegpt_api_key = self.config.get("codegpt_api_key") or os.getenv(
                "CODEGPT_API_KEY"
            )
            if not self.codegpt_api_key:
                raise ValueError("CodeGPT API key not configured")

    def _load_models(self):
        models_file = Path("config/ai_models.json")
        if models_file.exists():
            with open(models_file, "r") as f:
                self.models = json.load(f)

    async def analyze_vulnerability(
        self, scan_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze vulnerability using the configured AI provider"""
        try:
            start_time = datetime.now()
            request = self._prepare_analysis_request(scan_result)
            if cached := self._get_cached_analysis(request):
                return cached

            analysis = await self._get_analysis(scan_result)
            result = self._create_analysis_result(analysis, start_time)
            self._cache_analysis(request, result)
            return result
        except (json.JSONDecodeError, ValueError, OSError, aiohttp.ClientError) as e:
            logger.error(f"Vulnerability analysis failed: {str(e)}")
            raise

    def _prepare_analysis_request(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "content": json.dumps(scan_result),
            "context": {
                "scan_type": scan_result.get("scan_type"),
                "target": scan_result.get("target"),
            },
            "analysis_type": "vulnerability",
            "options": self.config.get("vulnerability_analysis", {}),
        }

    async def _get_analysis(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        if self.api_type == "bughunter":
            return await self._get_bughunter_analysis(scan_result)
        prompt = self._prepare_vulnerability_prompt(scan_result)
        if self.api_type == "openai":
            response = await self._get_openai_response(prompt)
        else:  # codegpt
            response = await self._get_codegpt_response(prompt)
        return self._parse_vulnerability_analysis(response)

    def _create_analysis_result(
        self, analysis: Dict[str, Any], start_time: datetime
    ) -> Dict[str, Any]:
        return {
            "analysis": analysis["analysis"],
            "recommendations": analysis["recommendations"],
            "confidence": analysis.get("confidence", 0.8),
            "timestamp": datetime.now().isoformat(),
            "duration": (datetime.now() - start_time).total_seconds(),
        }

    async def analyze_website(self, url: str) -> Dict[str, Any]:
        """Analyze website for vulnerabilities using BugHunter's local analysis"""
        try:
            content = await self._fetch_website_content(url)
            soup = BeautifulSoup(content, "html.parser")
            technologies = self._detect_technologies(content, soup)
            vulnerabilities = self._analyze_vulnerabilities(content, technologies)
            recommendations = self._generate_recommendations(
                technologies, vulnerabilities
            )
            return {
                "status": "success",
                "technologies": technologies,
                "vulnerabilities": vulnerabilities,
                "recommendations": recommendations,
            }
        except (aiohttp.ClientError, ValueError, OSError) as e:
            logger.error(f"Website analysis failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _fetch_website_content(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                return await response.text()

    async def _get_bughunter_analysis(
        self, scan_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get analysis using BugHunter's local AI"""
        url = scan_result.get("target_url")
        if not url:
            raise ValueError("Target URL not provided in scan result")
        website_analysis = await self.analyze_website(url)
        return {
            "analysis": {
                "vulnerabilities": [
                    {
                        "id": f"BH-{i + 1}",
                        "severity": vuln["severity"],
                        "analysis": f"Found {vuln['type']} vulnerability",
                        "impact": "Potential security risk",
                        "remediation": "Follow security best practices",
                    }
                    for i, vuln in enumerate(website_analysis["vulnerabilities"])
                ],
                "summary": f"Found {len(website_analysis['vulnerabilities'])} potential vulnerabilities",
            },
            "recommendations": [
                {
                    "priority": i + 1,
                    "action": rec,
                    "details": "Implement security measures",
                }
                for i, rec in enumerate(website_analysis["recommendations"])
            ],
            "confidence": 0.85,
        }

    async def _get_openai_response(self, prompt: str) -> str:
        """Get response from OpenAI API"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        response = await self.openai_client.chat.completions.create(
            model=self.models.get("openai_model", "gpt-4"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a security expert analyzing vulnerability scan results.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.config.get("temperature", 0.3),
            max_tokens=self.config.get("max_tokens", 2000),
        )
        return response.choices[0].message["content"]

    async def _get_codegpt_response(self, prompt: str) -> str:
        """Get response from CodeGPT API"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.codegpt_api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a security expert analyzing vulnerability scan results.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.config.get("temperature", 0.3),
                "max_tokens": self.config.get("max_tokens", 2000),
            }
            async with session.post(
                "https://api.codegpt.co/v1/chat/completions", headers=headers, json=data
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise RuntimeError(
                        f"CodeGPT API error: {result.get('error', {}).get('message', 'Unknown error')}"
                    )
                return result["choices"][0]["message"]["content"]

    def _detect_technologies(self, content: str, soup: BeautifulSoup) -> List[str]:
        """Detect technologies used in the website"""
        technologies = []
        for tech, patterns in self.technology_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    technologies.append(tech)
                    break
        meta_tags = soup.find_all("meta")
        scripts = soup.find_all("script")
        for tag in meta_tags + scripts:
            tag_str = str(tag)
            for tech, patterns in self.technology_patterns.items():
                if tech not in technologies:
                    for pattern in patterns:
                        if re.search(pattern, tag_str, re.IGNORECASE):
                            technologies.append(tech)
                            break
        return list(set(technologies))

    def _analyze_vulnerabilities(
        self, content: str, technologies: List[str]
    ) -> List[Dict]:
        """Analyze potential vulnerabilities"""
        vulnerabilities = []
        checks = [
            {
                "type": "information_disclosure",
                "patterns": [
                    r'(?:password|passwd|pwd).*[\'"][^\'"]+[\'"]',
                    r'(?:api[_-]?key|api[_-]?token)[^\'"]*[\'"][^\'"]+[\'"]',
                    r'(?:access[_-]?token|auth[_-]?token)[^\'"]*[\'"][^\'"]+[\'"]',
                ],
                "severity": "high",
            },
            {
                "type": "security_misconfiguration",
                "patterns": [
                    r"(?:ALLOW-FROM|SAMEORIGIN|DENY)",
                    r"(?:strict-transport-security-header)",
                    r"(?:content-security-policy)",
                ],
                "severity": "medium",
            },
            {
                "type": "injection_point",
                "patterns": [
                    r"(?:id|user|username|password|search|query)=[^&]+",
                    r"<input[^>]+(?:text|password|search)[^>]+>",
                    r"<form[^>]*>",
                ],
                "severity": "medium",
            },
        ]
        for check in checks:
            for pattern in check["patterns"]:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                vulnerabilities.extend(
                    [
                        {
                            "type": check["type"],
                            "severity": check["severity"],
                            "location": "source code",
                            "confidence": "medium",
                            "evidence": match.group(0),
                        }
                        for match in matches
                    ]
                )
        return vulnerabilities

    def _generate_recommendations(
        self, technologies: List[str], vulnerabilities: List[Dict]
    ) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        tech_recommendations = {
            "wordpress": [
                "Keep WordPress core, themes, and plugins updated",
                "Implement WordPress security hardening measures",
            ],
            "php": [
                "Ensure proper input validation and sanitization",
                "Use prepared statements for database queries",
            ],
            "java": [
                "Keep Java and all dependencies up to date",
                "Implement proper error handling",
            ],
            "python": [
                "Use the latest security features of your framework",
                "Implement proper input validation",
            ],
            "node.js": [
                "Keep Node.js and all dependencies up to date",
                "Implement security best practices",
            ],
            "database": [
                "Ensure proper database configuration",
                "Use encryption for sensitive data",
            ],
        }
        for tech in technologies:
            if tech in tech_recommendations:
                recommendations.extend(tech_recommendations[tech])
        vuln_types = {v["type"] for v in vulnerabilities}
        if "information_disclosure" in vuln_types:
            recommendations.append(
                "Review and secure sensitive information in source code"
            )
        if "security_misconfiguration" in vuln_types:
            recommendations.append(
                "Implement proper security headers and configurations"
            )
        if "injection_point" in vuln_types:
            recommendations.append("Implement input validation and output encoding")
        return list(set(recommendations))

    def _prepare_vulnerability_prompt(self, scan_result: Dict[str, Any]) -> str:
        """Prepare prompt for vulnerability analysis"""
        return f"""
        Please analyze the following vulnerability scan results and provide:
        1. A detailed analysis of each vulnerability found
        2. Risk assessment and potential impact
        3. Recommended remediation steps
        4. Priority order for addressing the vulnerabilities

        Scan Results:
        {json.dumps(scan_result, indent=2)}

        Please format your response as JSON with the following structure:
        {{
            "analysis": {{
                "vulnerabilities": [
                    {{
                        "id": "...",
                        "severity": "...",
                        "analysis": "...",
                        "impact": "...",
                        "remediation": "..."
                    }}
                ],
                "summary": "..."
            }},
            "recommendations": [
                {{
                    "priority": 1,
                    "action": "...",
                    "details": "..."
                }}
            ],
            "confidence": 0.95
        }}
        """

    def _parse_vulnerability_analysis(self, response: str) -> Dict[str, Any]:
        """Parse AI response for vulnerability analysis"""
        try:
            return json.loads(response)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse vulnerability analysis response: {str(e)}")
            raise

    def _get_cached_analysis(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached analysis result"""
        try:
            cache_key = self._generate_cache_key(request)
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                with open(cache_file, "r") as f:
                    cached = json.load(f)
                return cached
            return None
        except (json.JSONDecodeError, ValueError, OSError) as e:
            logger.error(f"Cache retrieval failed: {str(e)}")
            return None

    def _cache_analysis(self, request: Dict[str, Any], result: Dict[str, Any]):
        """Cache analysis result"""
        try:
            cache_key = self._generate_cache_key(request)
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, "w") as f:
                json.dump(result, f, indent=4)
        except (json.JSONDecodeError, ValueError, OSError) as e:
            logger.error(f"Cache storage failed: {str(e)}")

    def _generate_cache_key(self, request: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        content = f"{request['content']}_{request['analysis_type']}_{self.api_type}"
        return hashlib.md5(content.encode()).hexdigest()

    async def cleanup(self):
        """Cleanup resources"""
        try:
            self.initialized = False
            self.openai_client = None
            if hasattr(self, "session") and self.session:
                await self.session.close()
        except (aiohttp.ClientError, OSError) as e:
            logger.error(f"AI service cleanup failed: {str(e)}")
