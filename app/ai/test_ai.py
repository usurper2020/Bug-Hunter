def test_sentiment_analysis(ai_model):
    test_data = {
        "name": "Test Vulnerability",
        "description": "This is a test description for sentiment analysis.",
        "severity": "Medium"
    }
    result = ai_model.analyze_vulnerability(test_data)
    print("Sentiment Analysis Result:", result['sentiment'])

from ai_integration import AIIntegration as AIModel

# Assuming you have a way to instantiate the AIModel class
if __name__ == "__main__":
    model = AIModel()
    test_sentiment_analysis(model)
