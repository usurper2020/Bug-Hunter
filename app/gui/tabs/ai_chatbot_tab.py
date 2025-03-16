import re
import sys
from PyQt6 import QtWidgets, QtCore
from app.ai.ai import AIModel
from app.ai.ai_integration import AIIntegration
from PyQt6.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget

class AIChatbotTab(QWidget):
    """
    Tab widget providing AI chatbot functionality.

    This widget creates a simple chat interface with:
    - Text input area for user messages
    - Send button for message submission
    - Response display area for AI output
    - Integration with backend AI systems

    The chatbot specializes in providing vulnerability
    and security-related information.
    """

    def __init__(self):
        """
        Initialize the AI chatbot interface.

        Sets up:
        - UI components and layout
        - Message handling system
        - AI model integration
        - Response display area
        """
        super().__init__()
        self.setWindowTitle("AI Chatbot")

        # Create layout for the chatbot tab
        self.layout = QVBoxLayout()

        # Label for instructions
        self.instructions = QLabel("Enter your message to the AI:")
        self.layout.addWidget(self.instructions)

        # Text box for user input
        self.user_input = QTextEdit()
        self.layout.addWidget(self.user_input)

        # Button to send message
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        # Label to display AI response
        self.ai_response = QLabel("AI Response:")
        self.layout.addWidget(self.ai_response)

        # Set the layout for the tab
        self.setLayout(self.layout)

        # Initialize AI model and integration
        self.ai_model = AIModel()
        self.ai_integration = AIIntegration()

    def send_message(self):
        """
        Process and send user message to AI system.

        This method:
        1. Retrieves message from input field
        2. Sends to AI for processing
        3. Displays the response
        4. Clears input for next message
        """
        user_message = self.user_input.toPlainText()
        ai_response = self.get_ai_response(user_message)
        self.ai_response.setText(f"AI: {ai_response}")
        self.user_input.clear()

    def get_ai_response(self, message):
        """
        Get AI response for a given user message.

        Parameters:
        message (str): User's input message

        Returns:
        str: Formatted AI response with vulnerability
        information, or error message if no relevant
        information is found
        """
        # Use the AI integration to get a response based on user input
        response = self.ai_integration.get_response(message)
        if response:
            return f"Vulnerability Info: {response}"
        return "No information found for the given input."