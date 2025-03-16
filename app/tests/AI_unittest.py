import unittest
from unittest.mock import patch
from app.ai.ai import AIModel

class TestAIModel(unittest.TestCase):

    @patch('app.ai.ai.logger')
    def test_warm_up_model_failure(self, mock_logger):
        model = AIModel()
        model._warm_up_model()
        mock_logger.warning.assert_called_with("Model warm-up failed: Test exception")

    @patch('app.ai.ai.logger')
    def test_analyze_vulnerability_failure(self, mock_logger):
        model = AIModel()
        result = model.analyze_vulnerability({})
        self.assertIn("error", result)
        mock_logger.error.assert_called()

if __name__ == '__main__':
    unittest.main()