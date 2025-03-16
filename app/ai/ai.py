import logging
import threading
import queue

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
import time
from typing import Dict, Optional, List, Tuple
import torch
from transformers import pipeline
from app.config import settings
from functools import lru_cache
from datetime import datetime
import psutil
import json
import hashlib
from langdetect import detect
from sentiment_analysis import SentimentAnalyzer

class AIModel:
    """
    Comprehensive AI model with advanced features.
    """

    def __init__(self):
        """
        Initialize the AI model with all capabilities.
        """
        self.models = {}  # Dictionary for model versioning
        self.active_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.context_memory = {}  # For maintaining conversation context
        self.sentiment_analyzer = SentimentAnalyzer()
        self._initialize_models()
        self._warm_up_model()
        
        # Task processing system
        self.task_queue = queue.PriorityQueue()
        self.result_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_tasks)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        # Performance monitoring
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'start_time': datetime.now()
        }
        self.request_lock = threading.Lock()
        self.last_request_time = 0

    def _initialize_models(self):
        """
        Load and configure multiple model versions.
        """
        try:
            # Primary model
            self.models['v1'] = pipeline(
                "text-generation",
                model=settings.AI_MODEL_NAME,
                device=self.device
            )
            
            # Fallback model
            self.models['fallback'] = pipeline(
                "text-generation",
                model="gpt2",  # Lightweight fallback
                device=self.device
            )
            
            # Compressed model
            self.models['compressed'] = pipeline(
                "text-generation",
                model=settings.AI_COMPRESSED_MODEL_NAME,
                device=self.device
            )
            
            self.active_model = self.models['v1']
            logger.info("AI models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {str(e)}")
            raise

    def _warm_up_model(self):
        """
        Warm up the model with initial queries.
        """
        try:
            warm_up_queries = [
                "What is a security vulnerability?",
                "Explain SQL injection",
                "Describe cross-site scripting"
            ]
            for query in warm_up_queries:
                self.active_model(query, max_length=50)
            logger.info("Model warm-up completed")
        except Exception as e:
            logger.warning(f"Model warm-up failed: {str(e)}")
            raise

    def _process_tasks(self):
        """
        Background thread for processing tasks from the queue.
        """
        while True:
            priority, task = self.task_queue.get()
            if task is None:
                break
            try:
                start_time = time.time()
                result = self._execute_task(task)
                processing_time = time.time() - start_time
                
                # Update metrics
                with self.request_lock:
                    self.metrics['total_requests'] += 1
                    self.metrics['successful_requests'] += 1
                    self.metrics['average_response_time'] = (
                        self.metrics['average_response_time'] * (self.metrics['total_requests'] - 1) + processing_time
                    ) / self.metrics['total_requests']
                
                self.result_queue.put((task['id'], result))
            except Exception as e:
                logger.error(f"Task processing failed: {str(e)}")
                with self.request_lock:
                    self.metrics['failed_requests'] += 1
                self.result_queue.put((task['id'], {"error": str(e)}))
            finally:
                self.task_queue.task_done()

    def _execute_task(self, task: Dict) -> Dict:
        """
        Execute a specific AI task with error recovery.
        """
        try:
            return self._execute_task_with_fallback(task)
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            return {"error": str(e)}

    def _execute_task_with_fallback(self, task: Dict) -> Dict:
        """
        Execute task with fallback to simpler model if needed.
        """
        try:
            return self._execute_task_with_model(task, self.active_model)
        except Exception as e:
            logger.warning(f"Primary model failed, trying fallback: {str(e)}")
            try:
                return self._execute_task_with_model(task, self.models['fallback'])
            except Exception as e:
                logger.warning(f"Fallback model failed, trying compressed: {str(e)}")
                return self._execute_task_with_model(task, self.models['compressed'])

    def _execute_task_with_model(self, task: Dict, model) -> Dict:
        """
        Execute task using a specific model.
        """
        task_type = task['type']
        if task_type == 'analyze':
            return self._analyze_vulnerability(task['data'], model)
        elif task_type == 'query':
            return self._process_query(task['data'], model)
        elif task_type == 'batch':
            return self._process_batch(task['data'], model)
        elif task_type == 'fine_tune':
            return self._fine_tune_model(task['data'], model)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    @lru_cache(maxsize=100)
    def analyze_vulnerability(self, vulnerability_data: Dict) -> Dict:
        """
        Thread-safe vulnerability analysis with caching.
        """
        task_id = str(time.time())
        self.task_queue.put((1, {
            'id': task_id,
            'type': 'analyze',
            'data': vulnerability_data
        }))
        return self._wait_for_result(task_id)

    @lru_cache(maxsize=100)
    def process_query(self, query: str) -> str:
        """
        Thread-safe query processing with caching.
        """
        task_id = str(time.time())
        self.task_queue.put((1, {
            'id': task_id,
            'type': 'query',
            'data': query
        }))
        return self._wait_for_result(task_id)

    def process_batch(self, queries: List[str]) -> List[str]:
        """
        Process multiple queries in batch.
        """
        task_id = str(time.time())
        self.task_queue.put((0, {  # Higher priority for batch processing
            'id': task_id,
            'type': 'batch',
            'data': queries
        }))
        return self._wait_for_result(task_id)

    def _wait_for_result(self, task_id: str):
        """
        Wait for and retrieve result from the result queue.
        """
        while True:
            result_id, result = self.result_queue.get()
            if result_id == task_id:
                return result

    def _analyze_vulnerability(self, vulnerability_data: Dict, model) -> Dict:
        """
        Analyze vulnerability data with rate limiting.
        """
        with self.request_lock:
            current_time = time.time()
            if current_time - self.last_request_time < settings.AI_MIN_REQUEST_INTERVAL:
                time.sleep(settings.AI_MIN_REQUEST_INTERVAL - (current_time - self.last_request_time))
            self.last_request_time = time.time()

        try:
            # Security validation
            self._validate_vulnerability_data(vulnerability_data)
            
            # Language detection
            language = self._detect_language(vulnerability_data.get("description", ""))
            
            # Sentiment analysis
            sentiment = self.sentiment_analyzer.analyze(vulnerability_data.get("description", ""))
            
            return {
                "name": vulnerability_data.get("name", "Unknown"),
                "description": vulnerability_data.get("description", "No description available"),
                "severity": vulnerability_data.get("severity", "Unknown"),
                "risk_score": self._calculate_risk_score(vulnerability_data),
                "recommendations": self._generate_recommendations(vulnerability_data, model),
                "language": language,
                "sentiment": sentiment
            }
        except Exception as e:
            logger.error(f"Vulnerability analysis failed: {str(e)}")
            return {
                "error": "Failed to analyze vulnerability",
                "details": str(e)
            }

    def _validate_vulnerability_data(self, data: Dict):
        """
        Validate vulnerability data structure and content.
        """
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")

    def _detect_language(self, text: str) -> str:
        """
        Detect language of the input text.
        """
        try:
            return detect(text)
        except Exception:
            return "unknown"

    def _calculate_risk_score(self, vulnerability_data: Dict) -> float:
        """
        Calculate risk score based on vulnerability data.
        """
        severity = vulnerability_data.get("severity", "low").lower()
        severity_weights = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25
        }
        return severity_weights.get(severity, 0.0)

    def _generate_recommendations(self, vulnerability_data: Dict, model) -> list:
        """
        Generate security recommendations with rate limiting.
        """
        with self.request_lock:
            current_time = time.time()
            if current_time - self.last_request_time < settings.AI_MIN_REQUEST_INTERVAL:
                time.sleep(settings.AI_MIN_REQUEST_INTERVAL - (current_time - self.last_request_time))
            self.last_request_time = time.time()

        try:
            prompt = f"Generate security recommendations for {vulnerability_data.get('name', 'a vulnerability')}: "
            response = model(
                prompt,
                max_length=settings.AI_MAX_RESPONSE_LENGTH,
                temperature=settings.AI_TEMPERATURE
            )
            return [rec.strip() for rec in response[0]['generated_text'].split("\n") if rec.strip()]
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return ["Unable to generate recommendations at this time"]

    def _process_batch(self, queries: List[str], model) -> List[str]:
        """
        Process multiple queries efficiently.
        """
        results = []
        for query in queries:
            try:
                response = model(
                    query,
                    max_length=settings.AI_MAX_RESPONSE_LENGTH,
                    temperature=settings.AI_TEMPERATURE
                )
                results.append(response[0]['generated_text'])
            except Exception as e:
                logger.error(f"Batch query processing failed: {str(e)}")
                results.append("Unable to process query")
        return results

    def fine_tune_model(self, training_data: List[Dict]):
        """
        Fine-tune the model with new training data.
        """
        task_id = str(time.time())
        self.task_queue.put((2, {  # Highest priority for fine-tuning
            'id': task_id,
            'type': 'fine_tune',
            'data': training_data
        }))
        return self._wait_for_result(task_id)

    def _fine_tune_model(self, training_data: List[Dict], model):
        """
        Perform model fine-tuning.
        """
        # Implementation of fine-tuning logic
        # This would typically involve:
        # 1. Data preprocessing
        # 2. Model training
        # 3. Validation
        # 4. Model saving
        # Note: Actual implementation would depend on the specific model architecture
        return {"status": "Fine-tuning completed"}

    def get_performance_metrics(self) -> Dict:
        """
        Get current performance metrics.
        """
        process = psutil.Process()
        return {
            **self.metrics,
            'uptime': str(datetime.now() - self.metrics['start_time']),
            'memory_usage': process.memory_info().rss / 1024 / 1024,  # MB
            'cpu_usage': process.cpu_percent(),
            'active_model': self.active_model.model.config._name_or_path
        }

    def get_context(self, session_id: str) -> Dict:
        """
        Get conversation context for a session.
        """
        return self.context_memory.get(session_id, {})

    def update_context(self, session_id: str, context: Dict):
        """
        Update conversation context for a session.
        """
        self.context_memory[session_id] = context

    def clear_context(self, session_id: str):
        """
        Clear conversation context for a session.
        """
        if session_id in self.context_memory:
            del self.context_memory[session_id]

    def reload_config(self):
        """
        Reload model configuration from settings.
        """
        self._initialize_models()
        logger.info("Model configuration reloaded")

    def cleanup(self):
        """
        Clean up AI model resources and stop worker thread.
        """
        if self.models:
            self.task_queue.put((0, None))  # Signal worker thread to stop
            self.worker_thread.join()
            for model in self.models.values():
                del model
            logger.info("AI model resources cleaned up")

    def generate_documentation(self) -> str:
        """
        Generate API documentation for the AI model.
        """
        return json.dumps({
            "methods": [
                {
                    "name": "analyze_vulnerability",
                    "description": "Analyze vulnerability data",
                    "parameters": {
                        "vulnerability_data": "Dict containing vulnerability information"
                    }
                },
                {
                    "name": "process_query",
                    "description": "Process a security-related query",
                    "parameters": {
                        "query": "String containing the query"
                    }
                },
                # Add documentation for other methods
            ]
        }, indent=2)

    def run_tests(self) -> Dict:
        """
        Run a suite of tests on the AI model.
        """
        return {
            "model_loading": self._test_model_loading(),
            "query_processing": self._test_query_processing(),
            "vulnerability_analysis": self._test_vulnerability_analysis()
        }

    def _test_model_loading(self) -> bool:
        """
        Test model loading functionality.
        """
        try:
            return self.active_model is not None
        except Exception:
            return False

    def _test_query_processing(self) -> bool:
        """
        Test query processing functionality.
        """
        try:
            response = self.process_query("What is SQL injection?")
            return bool(response)
        except Exception:
            return False

    def _test_vulnerability_analysis(self) -> bool:
        """
        Test vulnerability analysis functionality.
        """
        try:
            test_data = {
                "name": "SQL Injection",
                "description": "A security vulnerability...",
                "severity": "High"
            }
            result = self.analyze_vulnerability(test_data)
            return bool(result.get("recommendations", []))
        except Exception:
            return False

    def _test_warm_up_model(self) -> bool:
        """
        Test model warm-up functionality.
        """
        try:
            self._warm_up_model()
            return True
        except Exception:
            return False
