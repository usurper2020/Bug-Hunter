import unittest
from unittest.mock import patch, MagicMock
from app.ai.ai import AIModel

class TestAIModel(unittest.TestCase):

    @patch('app.ai.ai.pipeline')
    @patch('app.ai.ai.settings')
    def setUp(self, mock_settings, mock_pipeline):
        # Mock settings
        mock_settings.AI_MODEL_NAME = "test-model"
        mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
        
        # Mock pipeline
        mock_pipeline.return_value = MagicMock()
        
        # Initialize AIModel
        self.ai_model = AIModel()

    @patch('app.ai.ai.logger')
    def test_warm_up_model_success(self, mock_logger):
        # Mock the active model to simulate successful responses
        self.ai_model.active_model = MagicMock()
        self.ai_model.active_model.return_value = [{"generated_text": "response"}]

        # Call the method
        self.ai_model._warm_up_model()

        # Check if the model was called with the warm-up queries
        warm_up_queries = [
            "What is a security vulnerability?",
            "Explain SQL injection",
            "Describe cross-site scripting"
        ]
        for query in warm_up_queries:
            self.ai_model.active_model.assert_any_call(query, max_length=50)

        # Check if the logger info was called
        mock_logger.info.assert_called_with("Model warm-up completed")

    @patch('app.ai.ai.logger')
    def test_warm_up_model_failure(self, mock_logger):
        # Mock the active model to raise an exception
        self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

        # Call the method
        self.ai_model._warm_up_model()

        # Check if the logger warning was called
        mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

        @patch('app.ai.ai.logger')
        def test_process_query_success(self, mock_logger):
            # Mock the active model to simulate successful response
            self.ai_model.active_model = MagicMock()
            self.ai_model.active_model.return_value = [{"generated_text": "response"}]
            query = "What is SQL injection?"

            # Call the method
            result = self.ai_model.process_query(query)

            # Check if the result is as expected
            self.assertEqual(result, "response")

        @patch('app.ai.ai.logger')
        def test_process_query_failure(self, mock_logger):
            # Mock the active model to raise an exception
            self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))
            query = "What is SQL injection?"

            # Call the method
            result = self.ai_model.process_query(query)

            # Check if the result is as expected
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Test exception")

        @patch('app.ai.ai.logger')
        def test_process_batch_success(self, mock_logger):
            # Mock the active model to simulate successful response
            self.ai_model.active_model = MagicMock()
            self.ai_model.active_model.return_value = [{"generated_text": "response"}]
            queries = ["What is SQL injection?", "Explain XSS"]

            # Call the method
            result = self.ai_model.process_batch(queries)

            # Check if the result is as expected
            self.assertEqual(result, ["response", "response"])

        @patch('app.ai.ai.logger')
        def test_process_batch_failure(self, mock_logger):
            # Mock the active model to raise an exception
            self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))
            queries = ["What is SQL injection?", "Explain XSS"]

            # Call the method
            result = self.ai_model.process_batch(queries)

            # Check if the result is as expected
            self.assertEqual(result, ["Unable to process query", "Unable to process query"])

        @patch('app.ai.ai.logger')
        def test_fine_tune_model_success(self, mock_logger):
            # Mock the active model to simulate successful response
            self.ai_model.active_model = MagicMock()
            training_data = [{"input": "data", "output": "result"}]

            # Call the method
            result = self.ai_model.fine_tune_model(training_data)

            # Check if the result is as expected
            self.assertEqual(result, {"status": "Fine-tuning completed"})

        @patch('app.ai.ai.logger')
        def test_fine_tune_model_failure(self, mock_logger):
            # Mock the active model to raise an exception
            self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))
            training_data = [{"input": "data", "output": "result"}]

            # Call the method
            result = self.ai_model.fine_tune_model(training_data)

            # Check if the result is as expected
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Test exception")

        @patch('app.ai.ai.logger')
        def test_initialize_models_success(self, mock_logger):
            # Mock the pipeline to simulate successful model loading
            self.ai_model.models['v1'] = MagicMock()
            self.ai_model.models['fallback'] = MagicMock()
            self.ai_model.models['compressed'] = MagicMock()

            # Call the method
            self.ai_model._initialize_models()

            # Check if the logger info was called
            mock_logger.info.assert_called_with("AI models initialized successfully")

        @patch('app.ai.ai.logger')
        def test_initialize_models_failure(self, mock_logger):
            # Mock the pipeline to raise an exception
            with patch('app.ai.ai.pipeline', side_effect=Exception("Test exception")):
                with self.assertRaises(Exception):
                    self.ai_model._initialize_models()

            # Check if the logger error was called
            mock_logger.error.assert_called_with("Failed to initialize AI models: Test exception")

        @patch('app.ai.ai.logger')
        def test_execute_task_with_fallback_success(self, mock_logger):
            # Mock the active model to simulate successful response
            self.ai_model.active_model = MagicMock()
            self.ai_model.models['fallback'] = MagicMock()
            self.ai_model.models['compressed'] = MagicMock()
            task = {'type': 'query', 'data': 'test query'}

            # Call the method
            result = self.ai_model._execute_task_with_fallback(task)

            # Check if the result is as expected
            self.assertIsNotNone(result)

        @patch('app.ai.ai.logger')
        def test_execute_task_with_fallback_failure(self, mock_logger):
            # Mock the active model and fallback models to raise exceptions
            self.ai_model.active_model = MagicMock(side_effect=Exception("Primary model failure"))
            self.ai_model.models['fallback'] = MagicMock(side_effect=Exception("Fallback model failure"))
            self.ai_model.models['compressed'] = MagicMock(return_value={"generated_text": "response"})
            task = {'type': 'query', 'data': 'test query'}

            # Call the method
            result = self.ai_model._execute_task_with_fallback(task)

            # Check if the result is as expected
            self.assertEqual(result, {"generated_text": "response"})

        @patch('app.ai.ai.logger')
        def test_analyze_vulnerability_success(self, mock_logger):
            # Mock the active model to simulate successful response
            self.ai_model.active_model = MagicMock()
            vulnerability_data = {
                "name": "SQL Injection",
                "description": "A security vulnerability...",
                "severity": "High"
            }

            # Call the method
            result = self.ai_model.analyze_vulnerability(vulnerability_data)

            # Check if the result is as expected
            self.assertIn("recommendations", result)

        @patch('app.ai.ai.logger')
        def test_analyze_vulnerability_failure(self, mock_logger):
            # Mock the active model to raise an exception
            self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))
            vulnerability_data = {
                "name": "SQL Injection",
                "description": "A security vulnerability...",
                "severity": "High"
            }

            # Call the method
            result = self.ai_model.analyze_vulnerability(vulnerability_data)

            # Check if the result is as expected
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Failed to analyze vulnerability")

            class TestAIModel(unittest.TestCase):

                @patch('app.ai.ai.pipeline')
                @patch('app.ai.ai.settings')
                def setUp(self, mock_settings, mock_pipeline):
                    # Mock settings
                    mock_settings.AI_MODEL_NAME = "test-model"
                    mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                    
                    # Mock pipeline
                    mock_pipeline.return_value = MagicMock()
                    
                    # Initialize AIModel
                    self.ai_model = AIModel()

                @patch('app.ai.ai.logger')
                def test_warm_up_model_success(self, mock_logger):
                    # Mock the active model to simulate successful responses
                    self.ai_model.active_model = MagicMock()
                    self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                    # Call the method
                    self.ai_model._warm_up_model()

                    # Check if the model was called with the warm-up queries
                    warm_up_queries = [
                        "What is a security vulnerability?",
                        "Explain SQL injection",
                        "Describe cross-site scripting"
                    ]
                    for query in warm_up_queries:
                        self.ai_model.active_model.assert_any_call(query, max_length=50)

                    # Check if the logger info was called
                    mock_logger.info.assert_called_with("Model warm-up completed")

                @patch('app.ai.ai.logger')
                def test_warm_up_model_failure(self, mock_logger):
                    # Mock the active model to raise an exception
                    self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                    # Call the method
                    self.ai_model._warm_up_model()

                    # Check if the logger warning was called
                    mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

            if __name__ == '__main__':
                unittest.main()

                class TestAIModel(unittest.TestCase):

                    @patch('app.ai.ai.pipeline')
                    @patch('app.ai.ai.settings')
                    def setUp(self, mock_settings, mock_pipeline):
                        # Mock settings
                        mock_settings.AI_MODEL_NAME = "test-model"
                        mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                        
                        # Mock pipeline
                        mock_pipeline.return_value = MagicMock()
                        
                        # Initialize AIModel
                        self.ai_model = AIModel()

                    @patch('app.ai.ai.logger')
                    def test_warm_up_model_success(self, mock_logger):
                        # Mock the active model to simulate successful responses
                        self.ai_model.active_model = MagicMock()
                        self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                        # Call the method
                        self.ai_model._warm_up_model()

                        # Check if the model was called with the warm-up queries
                        warm_up_queries = [
                            "What is a security vulnerability?",
                            "Explain SQL injection",
                            "Describe cross-site scripting"
                        ]
                        for query in warm_up_queries:
                            self.ai_model.active_model.assert_any_call(query, max_length=50)

                        # Check if the logger info was called
                        mock_logger.info.assert_called_with("Model warm-up completed")

                    @patch('app.ai.ai.logger')
                    def test_warm_up_model_failure(self, mock_logger):
                        # Mock the active model to raise an exception
                        self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                        # Call the method
                        self.ai_model._warm_up_model()

                        # Check if the logger warning was called
                        mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                if __name__ == '__main__':
                    unittest.main()

                    class TestAIModel(unittest.TestCase):

                        @patch('app.ai.ai.pipeline')
                        @patch('app.ai.ai.settings')
                        def setUp(self, mock_settings, mock_pipeline):
                            # Mock settings
                            mock_settings.AI_MODEL_NAME = "test-model"
                            mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                            
                            # Mock pipeline
                            mock_pipeline.return_value = MagicMock()
                            
                            # Initialize AIModel
                            self.ai_model = AIModel()

                        @patch('app.ai.ai.logger')
                        def test_warm_up_model_success(self, mock_logger):
                            # Mock the active model to simulate successful responses
                            self.ai_model.active_model = MagicMock()
                            self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                            # Call the method
                            self.ai_model._warm_up_model()

                            # Check if the model was called with the warm-up queries
                            warm_up_queries = [
                                "What is a security vulnerability?",
                                "Explain SQL injection",
                                "Describe cross-site scripting"
                            ]
                            for query in warm_up_queries:
                                self.ai_model.active_model.assert_any_call(query, max_length=50)

                            # Check if the logger info was called
                            mock_logger.info.assert_called_with("Model warm-up completed")

                        @patch('app.ai.ai.logger')
                        def test_warm_up_model_failure(self, mock_logger):
                            # Mock the active model to raise an exception
                            self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                            # Call the method
                            self.ai_model._warm_up_model()

                            # Check if the logger warning was called
                            mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                    if __name__ == '__main__':
                        unittest.main()

                        class TestAIModel(unittest.TestCase):

                            @patch('app.ai.ai.pipeline')
                            @patch('app.ai.ai.settings')
                            def setUp(self, mock_settings, mock_pipeline):
                                # Mock settings
                                mock_settings.AI_MODEL_NAME = "test-model"
                                mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                
                                # Mock pipeline
                                mock_pipeline.return_value = MagicMock()
                                
                                # Initialize AIModel
                                self.ai_model = AIModel()

                            @patch('app.ai.ai.logger')
                            def test_warm_up_model_success(self, mock_logger):
                                # Mock the active model to simulate successful responses
                                self.ai_model.active_model = MagicMock()
                                self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                # Call the method
                                self.ai_model._warm_up_model()

                                # Check if the model was called with the warm-up queries
                                warm_up_queries = [
                                    "What is a security vulnerability?",
                                    "Explain SQL injection",
                                    "Describe cross-site scripting"
                                ]
                                for query in warm_up_queries:
                                    self.ai_model.active_model.assert_any_call(query, max_length=50)

                                # Check if the logger info was called
                                mock_logger.info.assert_called_with("Model warm-up completed")

                            @patch('app.ai.ai.logger')
                            def test_warm_up_model_failure(self, mock_logger):
                                # Mock the active model to raise an exception
                                self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                # Call the method
                                self.ai_model._warm_up_model()

                                # Check if the logger warning was called
                                mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                        if __name__ == '__main__':
                            unittest.main()

                            class TestAIModel(unittest.TestCase):

                                @patch('app.ai.ai.pipeline')
                                @patch('app.ai.ai.settings')
                                def setUp(self, mock_settings, mock_pipeline):
                                    # Mock settings
                                    mock_settings.AI_MODEL_NAME = "test-model"
                                    mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                    
                                    # Mock pipeline
                                    mock_pipeline.return_value = MagicMock()
                                    
                                    # Initialize AIModel
                                    self.ai_model = AIModel()

                                @patch('app.ai.ai.logger')
                                def test_warm_up_model_success(self, mock_logger):
                                    # Mock the active model to simulate successful responses
                                    self.ai_model.active_model = MagicMock()
                                    self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                    # Call the method
                                    self.ai_model._warm_up_model()

                                    # Check if the model was called with the warm-up queries
                                    warm_up_queries = [
                                        "What is a security vulnerability?",
                                        "Explain SQL injection",
                                        "Describe cross-site scripting"
                                    ]
                                    for query in warm_up_queries:
                                        self.ai_model.active_model.assert_any_call(query, max_length=50)

                                    # Check if the logger info was called
                                    mock_logger.info.assert_called_with("Model warm-up completed")

                                @patch('app.ai.ai.logger')
                                def test_warm_up_model_failure(self, mock_logger):
                                    # Mock the active model to raise an exception
                                    self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                    # Call the method
                                    self.ai_model._warm_up_model()

                                    # Check if the logger warning was called
                                    mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                            if __name__ == '__main__':
                                unittest.main()

                                class TestAIModel(unittest.TestCase):

                                    @patch('app.ai.ai.pipeline')
                                    @patch('app.ai.ai.settings')
                                    def setUp(self, mock_settings, mock_pipeline):
                                        # Mock settings
                                        mock_settings.AI_MODEL_NAME = "test-model"
                                        mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                        
                                        # Mock pipeline
                                        mock_pipeline.return_value = MagicMock()
                                        
                                        # Initialize AIModel
                                        self.ai_model = AIModel()

                                    @patch('app.ai.ai.logger')
                                    def test_warm_up_model_success(self, mock_logger):
                                        # Mock the active model to simulate successful responses
                                        self.ai_model.active_model = MagicMock()
                                        self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                        # Call the method
                                        self.ai_model._warm_up_model()

                                        # Check if the model was called with the warm-up queries
                                        warm_up_queries = [
                                            "What is a security vulnerability?",
                                            "Explain SQL injection",
                                            "Describe cross-site scripting"
                                        ]
                                        for query in warm_up_queries:
                                            self.ai_model.active_model.assert_any_call(query, max_length=50)

                                        # Check if the logger info was called
                                        mock_logger.info.assert_called_with("Model warm-up completed")

                                    @patch('app.ai.ai.logger')
                                    def test_warm_up_model_failure(self, mock_logger):
                                        # Mock the active model to raise an exception
                                        self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                        # Call the method
                                        self.ai_model._warm_up_model()

                                        # Check if the logger warning was called
                                        mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                                if __name__ == '__main__':
                                    unittest.main()

                                    class TestAIModel(unittest.TestCase):

                                        @patch('app.ai.ai.pipeline')
                                        @patch('app.ai.ai.settings')
                                        def setUp(self, mock_settings, mock_pipeline):
                                            # Mock settings
                                            mock_settings.AI_MODEL_NAME = "test-model"
                                            mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                            
                                            # Mock pipeline
                                            mock_pipeline.return_value = MagicMock()
                                            
                                            # Initialize AIModel
                                            self.ai_model = AIModel()

                                        @patch('app.ai.ai.logger')
                                        def test_warm_up_model_success(self, mock_logger):
                                            # Mock the active model to simulate successful responses
                                            self.ai_model.active_model = MagicMock()
                                            self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                            # Call the method
                                            self.ai_model._warm_up_model()

                                            # Check if the model was called with the warm-up queries
                                            warm_up_queries = [
                                                "What is a security vulnerability?",
                                                "Explain SQL injection",
                                                "Describe cross-site scripting"
                                            ]
                                            for query in warm_up_queries:
                                                self.ai_model.active_model.assert_any_call(query, max_length=50)

                                            # Check if the logger info was called
                                            mock_logger.info.assert_called_with("Model warm-up completed")

                                        @patch('app.ai.ai.logger')
                                        def test_warm_up_model_failure(self, mock_logger):
                                            # Mock the active model to raise an exception
                                            self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                            # Call the method
                                            self.ai_model._warm_up_model()

                                            # Check if the logger warning was called
                                            mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                                    if __name__ == '__main__':
                                        unittest.main()

                                        class TestAIModel(unittest.TestCase):

                                            @patch('app.ai.ai.pipeline')
                                            @patch('app.ai.ai.settings')
                                            def setUp(self, mock_settings, mock_pipeline):
                                                # Mock settings
                                                mock_settings.AI_MODEL_NAME = "test-model"
                                                mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                                
                                                # Mock pipeline
                                                mock_pipeline.return_value = MagicMock()
                                                
                                                # Initialize AIModel
                                                self.ai_model = AIModel()

                                            @patch('app.ai.ai.logger')
                                            def test_warm_up_model_success(self, mock_logger):
                                                # Mock the active model to simulate successful responses
                                                self.ai_model.active_model = MagicMock()
                                                self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                                # Call the method
                                                self.ai_model._warm_up_model()

                                                # Check if the model was called with the warm-up queries
                                                warm_up_queries = [
                                                    "What is a security vulnerability?",
                                                    "Explain SQL injection",
                                                    "Describe cross-site scripting"
                                                ]
                                                for query in warm_up_queries:
                                                    self.ai_model.active_model.assert_any_call(query, max_length=50)

                                                # Check if the logger info was called
                                                mock_logger.info.assert_called_with("Model warm-up completed")

                                            @patch('app.ai.ai.logger')
                                            def test_warm_up_model_failure(self, mock_logger):
                                                # Mock the active model to raise an exception
                                                self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                                # Call the method
                                                self.ai_model._warm_up_model()

                                                # Check if the logger warning was called
                                                mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                                        if __name__ == '__main__':
                                            unittest.main()

                                            class TestAIModel(unittest.TestCase):

                                                @patch('app.ai.ai.pipeline')
                                                @patch('app.ai.ai.settings')
                                                def setUp(self, mock_settings, mock_pipeline):
                                                    # Mock settings
                                                    mock_settings.AI_MODEL_NAME = "test-model"
                                                    mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                                    
                                                    # Mock pipeline
                                                    mock_pipeline.return_value = MagicMock()
                                                    
                                                    # Initialize AIModel
                                                    self.ai_model = AIModel()

                                                @patch('app.ai.ai.logger')
                                                def test_warm_up_model_success(self, mock_logger):
                                                    # Mock the active model to simulate successful responses
                                                    self.ai_model.active_model = MagicMock()
                                                    self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                                    # Call the method
                                                    self.ai_model._warm_up_model()

                                                    # Check if the model was called with the warm-up queries
                                                    warm_up_queries = [
                                                        "What is a security vulnerability?",
                                                        "Explain SQL injection",
                                                        "Describe cross-site scripting"
                                                    ]
                                                    for query in warm_up_queries:
                                                        self.ai_model.active_model.assert_any_call(query, max_length=50)

                                                    # Check if the logger info was called
                                                    mock_logger.info.assert_called_with("Model warm-up completed")

                                                @patch('app.ai.ai.logger')
                                                def test_warm_up_model_failure(self, mock_logger):
                                                    # Mock the active model to raise an exception
                                                    self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                                    # Call the method
                                                    self.ai_model._warm_up_model()

                                                    # Check if the logger warning was called
                                                    mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                                            if __name__ == '__main__':
                                                unittest.main()

                                                class TestAIModel(unittest.TestCase):

                                                    @patch('app.ai.ai.pipeline')
                                                    @patch('app.ai.ai.settings')
                                                    def setUp(self, mock_settings, mock_pipeline):
                                                        # Mock settings
                                                        mock_settings.AI_MODEL_NAME = "test-model"
                                                        mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                                        
                                                        # Mock pipeline
                                                        mock_pipeline.return_value = MagicMock()
                                                        
                                                        # Initialize AIModel
                                                        self.ai_model = AIModel()

                                                    @patch('app.ai.ai.logger')
                                                    def test_warm_up_model_success(self, mock_logger):
                                                        # Mock the active model to simulate successful responses
                                                        self.ai_model.active_model = MagicMock()
                                                        self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                                        # Call the method
                                                        self.ai_model._warm_up_model()

                                                        # Check if the model was called with the warm-up queries
                                                        warm_up_queries = [
                                                            "What is a security vulnerability?",
                                                            "Explain SQL injection",
                                                            "Describe cross-site scripting"
                                                        ]
                                                        for query in warm_up_queries:
                                                            self.ai_model.active_model.assert_any_call(query, max_length=50)

                                                        # Check if the logger info was called
                                                        mock_logger.info.assert_called_with("Model warm-up completed")

                                                    @patch('app.ai.ai.logger')
                                                    def test_warm_up_model_failure(self, mock_logger):
                                                        # Mock the active model to raise an exception
                                                        self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                                        # Call the method
                                                        self.ai_model._warm_up_model()

                                                        # Check if the logger warning was called
                                                        mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                                                if __name__ == '__main__':
                                                    unittest.main()

                                                    class TestAIModel(unittest.TestCase):

                                                        @patch('app.ai.ai.pipeline')
                                                        @patch('app.ai.ai.settings')
                                                        def setUp(self, mock_settings, mock_pipeline):
                                                            # Mock settings
                                                            mock_settings.AI_MODEL_NAME = "test-model"
                                                            mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                                            
                                                            # Mock pipeline
                                                            mock_pipeline.return_value = MagicMock()
                                                            
                                                            # Initialize AIModel
                                                            self.ai_model = AIModel()

                                                        @patch('app.ai.ai.logger')
                                                        def test_warm_up_model_success(self, mock_logger):
                                                            # Mock the active model to simulate successful responses
                                                            self.ai_model.active_model = MagicMock()
                                                            self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                                            # Call the method
                                                            self.ai_model._warm_up_model()

                                                            # Check if the model was called with the warm-up queries
                                                            warm_up_queries = [
                                                                "What is a security vulnerability?",
                                                                "Explain SQL injection",
                                                                "Describe cross-site scripting"
                                                            ]
                                                            for query in warm_up_queries:
                                                                self.ai_model.active_model.assert_any_call(query, max_length=50)

                                                            # Check if the logger info was called
                                                            mock_logger.info.assert_called_with("Model warm-up completed")

                                                        @patch('app.ai.ai.logger')
                                                        def test_warm_up_model_failure(self, mock_logger):
                                                            # Mock the active model to raise an exception
                                                            self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                                            # Call the method
                                                            self.ai_model._warm_up_model()

                                                            # Check if the logger warning was called
                                                            mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                                                    if __name__ == '__main__':
                                                        unittest.main()

                                                        class TestAIModel(unittest.TestCase):

                                                            @patch('app.ai.ai.pipeline')
                                                            @patch('app.ai.ai.settings')
                                                            def setUp(self, mock_settings, mock_pipeline):
                                                                # Mock settings
                                                                mock_settings.AI_MODEL_NAME = "test-model"
                                                                mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                                                
                                                                # Mock pipeline
                                                                mock_pipeline.return_value = MagicMock()
                                                                
                                                                # Initialize AIModel
                                                                self.ai_model = AIModel()

                                                            @patch('app.ai.ai.logger')
                                                            def test_warm_up_model_success(self, mock_logger):
                                                                # Mock the active model to simulate successful responses
                                                                self.ai_model.active_model = MagicMock()
                                                                self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                                                # Call the method
                                                                self.ai_model._warm_up_model()

                                                                # Check if the model was called with the warm-up queries
                                                                warm_up_queries = [
                                                                    "What is a security vulnerability?",
                                                                    "Explain SQL injection",
                                                                    "Describe cross-site scripting"
                                                                ]
                                                                for query in warm_up_queries:
                                                                    self.ai_model.active_model.assert_any_call(query, max_length=50)

                                                                # Check if the logger info was called
                                                                mock_logger.info.assert_called_with("Model warm-up completed")

                                                            @patch('app.ai.ai.logger')
                                                            def test_warm_up_model_failure(self, mock_logger):
                                                                # Mock the active model to raise an exception
                                                                self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                                                # Call the method
                                                                self.ai_model._warm_up_model()

                                                                # Check if the logger warning was called
                                                                mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                                                        if __name__ == '__main__':
                                                            class TestAIModel(unittest.TestCase):

                                                                @patch('app.ai.ai.pipeline')
                                                                @patch('app.ai.ai.settings')
                                                                def setUp(self, mock_settings, mock_pipeline):
                                                                    # Mock settings
                                                                    mock_settings.AI_MODEL_NAME = "test-model"
                                                                    mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                                                    
                                                                    # Mock pipeline
                                                                    mock_pipeline.return_value = MagicMock()
                                                                    
                                                                    # Initialize AIModel
                                                                    self.ai_model = AIModel()

                                                                @patch('app.ai.ai.logger')
                                                                def test_warm_up_model_success(self, mock_logger):
                                                                    # Mock the active model to simulate successful responses
                                                                    self.ai_model.active_model = MagicMock()
                                                                    self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                                                    # Call the method
                                                                    self.ai_model._warm_up_model()

                                                                    # Check if the model was called with the warm-up queries
                                                                    warm_up_queries = [
                                                                        "What is a security vulnerability?",
                                                                        "Explain SQL injection",
                                                                        "Describe cross-site scripting"
                                                                    ]
                                                                    for query in warm_up_queries:
                                                                        self.ai_model.active_model.assert_any_call(query, max_length=50)

                                                                    # Check if the logger info was called
                                                                    mock_logger.info.assert_called_with("Model warm-up completed")

                                                                @patch('app.ai.ai.logger')
                                                                def test_warm_up_model_failure(self, mock_logger):
                                                                    # Mock the active model to raise an exception
                                                                    self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                                                    # Call the method
                                                                    self.ai_model._warm_up_model()

                                                                    # Check if the logger warning was called
                                                                    mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                                                            if __name__ == '__main__':
                                                                class TestAIModel(unittest.TestCase):

                                                                    @patch('app.ai.ai.pipeline')
                                                                    @patch('app.ai.ai.settings')
                                                                    def setUp(self, mock_settings, mock_pipeline):
                                                                        # Mock settings
                                                                        mock_settings.AI_MODEL_NAME = "test-model"
                                                                        mock_settings.AI_COMPRESSED_MODEL_NAME = "test-compressed-model"
                                                                        
                                                                        # Mock pipeline
                                                                        mock_pipeline.return_value = MagicMock()
                                                                        
                                                                        # Initialize AIModel
                                                                        self.ai_model = AIModel()

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_warm_up_model_success(self, mock_logger):
                                                                        # Mock the active model to simulate successful responses
                                                                        self.ai_model.active_model = MagicMock()
                                                                        self.ai_model.active_model.return_value = [{"generated_text": "response"}]

                                                                        # Call the method
                                                                        self.ai_model._warm_up_model()

                                                                        # Check if the model was called with the warm-up queries
                                                                        warm_up_queries = [
                                                                            "What is a security vulnerability?",
                                                                            "Explain SQL injection",
                                                                            "Describe cross-site scripting"
                                                                        ]
                                                                        for query in warm_up_queries:
                                                                            self.ai_model.active_model.assert_any_call(query, max_length=50)

                                                                        # Check if the logger info was called
                                                                        mock_logger.info.assert_called_with("Model warm-up completed")

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_warm_up_model_failure(self, mock_logger):
                                                                        # Mock the active model to raise an exception
                                                                        self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))

                                                                        # Call the method
                                                                        self.ai_model._warm_up_model()

                                                                        # Check if the logger warning was called
                                                                        mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_process_query_success(self, mock_logger):
                                                                        # Mock the active model to simulate successful response
                                                                        self.ai_model.active_model = MagicMock()
                                                                        self.ai_model.active_model.return_value = [{"generated_text": "response"}]
                                                                        query = "What is SQL injection?"

                                                                        # Call the method
                                                                        result = self.ai_model.process_query(query)

                                                                        # Check if the result is as expected
                                                                        self.assertEqual(result, "response")

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_process_query_failure(self, mock_logger):
                                                                        # Mock the active model to raise an exception
                                                                        self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))
                                                                        query = "What is SQL injection?"

                                                                        # Call the method
                                                                        result = self.ai_model.process_query(query)

                                                                        # Check if the result is as expected
                                                                        self.assertIn("error", result)
                                                                        self.assertEqual(result["error"], "Test exception")

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_process_batch_success(self, mock_logger):
                                                                        # Mock the active model to simulate successful response
                                                                        self.ai_model.active_model = MagicMock()
                                                                        self.ai_model.active_model.return_value = [{"generated_text": "response"}]
                                                                        queries = ["What is SQL injection?", "Explain XSS"]

                                                                        # Call the method
                                                                        result = self.ai_model.process_batch(queries)

                                                                        # Check if the result is as expected
                                                                        self.assertEqual(result, ["response", "response"])

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_process_batch_failure(self, mock_logger):
                                                                        # Mock the active model to raise an exception
                                                                        self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))
                                                                        queries = ["What is SQL injection?", "Explain XSS"]

                                                                        # Call the method
                                                                        result = self.ai_model.process_batch(queries)

                                                                        # Check if the result is as expected
                                                                        self.assertEqual(result, ["Unable to process query", "Unable to process query"])

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_fine_tune_model_success(self, mock_logger):
                                                                        # Mock the active model to simulate successful response
                                                                        self.ai_model.active_model = MagicMock()
                                                                        training_data = [{"input": "data", "output": "result"}]

                                                                        # Call the method
                                                                        result = self.ai_model.fine_tune_model(training_data)

                                                                        # Check if the result is as expected
                                                                        self.assertEqual(result, {"status": "Fine-tuning completed"})

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_fine_tune_model_failure(self, mock_logger):
                                                                        # Mock the active model to raise an exception
                                                                        self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))
                                                                        training_data = [{"input": "data", "output": "result"}]

                                                                        # Call the method
                                                                        result = self.ai_model.fine_tune_model(training_data)

                                                                        # Check if the result is as expected
                                                                        self.assertIn("error", result)
                                                                        self.assertEqual(result["error"], "Test exception")

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_initialize_models_success(self, mock_logger):
                                                                        # Mock the pipeline to simulate successful model loading
                                                                        self.ai_model.models['v1'] = MagicMock()
                                                                        self.ai_model.models['fallback'] = MagicMock()
                                                                        self.ai_model.models['compressed'] = MagicMock()

                                                                        # Call the method
                                                                        self.ai_model._initialize_models()

                                                                        # Check if the logger info was called
                                                                        mock_logger.info.assert_called_with("AI models initialized successfully")

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_initialize_models_failure(self, mock_logger):
                                                                        # Mock the pipeline to raise an exception
                                                                        with patch('app.ai.ai.pipeline', side_effect=Exception("Test exception")):
                                                                            with self.assertRaises(Exception):
                                                                                self.ai_model._initialize_models()

                                                                        # Check if the logger error was called
                                                                        mock_logger.error.assert_called_with("Failed to initialize AI models: Test exception")

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_execute_task_with_fallback_success(self, mock_logger):
                                                                        # Mock the active model to simulate successful response
                                                                        self.ai_model.active_model = MagicMock()
                                                                        self.ai_model.models['fallback'] = MagicMock()
                                                                        self.ai_model.models['compressed'] = MagicMock()
                                                                        task = {'type': 'query', 'data': 'test query'}

                                                                        # Call the method
                                                                        result = self.ai_model._execute_task_with_fallback(task)

                                                                        # Check if the result is as expected
                                                                        self.assertIsNotNone(result)

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_execute_task_with_fallback_failure(self, mock_logger):
                                                                        # Mock the active model and fallback models to raise exceptions
                                                                        self.ai_model.active_model = MagicMock(side_effect=Exception("Primary model failure"))
                                                                        self.ai_model.models['fallback'] = MagicMock(side_effect=Exception("Fallback model failure"))
                                                                        self.ai_model.models['compressed'] = MagicMock(return_value={"generated_text": "response"})
                                                                        task = {'type': 'query', 'data': 'test query'}

                                                                        # Call the method
                                                                        result = self.ai_model._execute_task_with_fallback(task)

                                                                        # Check if the result is as expected
                                                                        self.assertEqual(result, {"generated_text": "response"})

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_analyze_vulnerability_success(self, mock_logger):
                                                                        # Mock the active model to simulate successful response
                                                                        self.ai_model.active_model = MagicMock()
                                                                        vulnerability_data = {
                                                                            "name": "SQL Injection",
                                                                            "description": "A security vulnerability...",
                                                                            "severity": "High"
                                                                        }

                                                                        # Call the method
                                                                        result = self.ai_model.analyze_vulnerability(vulnerability_data)

                                                                        # Check if the result is as expected
                                                                        self.assertIn("recommendations", result)

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_analyze_vulnerability_failure(self, mock_logger):
                                                                        # Mock the active model to raise an exception
                                                                        self.ai_model.active_model = MagicMock(side_effect=Exception("Test exception"))
                                                                        vulnerability_data = {
                                                                            "name": "SQL Injection",
                                                                            "description": "A security vulnerability...",
                                                                            "severity": "High"
                                                                        }

                                                                        # Call the method
                                                                        result = self.ai_model.analyze_vulnerability(vulnerability_data)

                                                                        # Check if the result is as expected
                                                                        self.assertIn("error", result)
                                                                        self.assertEqual(result["error"], "Failed to analyze vulnerability")

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_get_performance_metrics(self, mock_logger):
                                                                        # Mock psutil process
                                                                        with patch('app.ai.ai.psutil.Process') as mock_process:
                                                                            mock_process.return_value.memory_info.return_value.rss = 1024 * 1024 * 100  # 100 MB
                                                                            mock_process.return_value.cpu_percent.return_value = 10.0

                                                                            # Call the method
                                                                            metrics = self.ai_model.get_performance_metrics()

                                                                            # Check if the metrics are as expected
                                                                            self.assertIn('memory_usage', metrics)
                                                                            self.assertIn('cpu_usage', metrics)
                                                                            self.assertIn('uptime', metrics)
                                                                            self.assertIn('active_model', metrics)

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_reload_config(self, mock_logger):
                                                                        # Mock the initialize models method
                                                                        self.ai_model._initialize_models = MagicMock()

                                                                        # Call the method
                                                                        self.ai_model.reload_config()

                                                                        # Check if the initialize models method was called
                                                                        self.ai_model._initialize_models.assert_called_once()

                                                                        # Check if the logger info was called
                                                                        mock_logger.info.assert_called_with("Model configuration reloaded")

                                                                    @patch('app.ai.ai.logger')
                                                                    def test_cleanup(self, mock_logger):
                                                                        # Mock the worker thread and models
                                                                        self.ai_model.worker_thread = MagicMock()
                                                                        self.ai_model.models = {'v1': MagicMock(), 'fallback': MagicMock(), 'compressed': MagicMock()}

                                                                        # Call the method
                                                                        self.ai_model.cleanup()

                                                                        # Check if the worker thread join was called
                                                                        self.ai_model.worker_thread.join.assert_called_once()

                                                                        # Check if the models were deleted
                                                                        self.assertEqual(self.ai_model.models, {})

                                                                        # Check if the logger info was called
                                                                        mock_logger.info.assert_called_with("AI model resources cleaned up")

                                                                if __name__ == '__main__':
                                                                    unittest.main()




if __name__ == '__main__':
    unittest.main()