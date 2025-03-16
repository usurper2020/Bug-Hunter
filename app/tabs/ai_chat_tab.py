from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from app.core.logger_config import get_logger

class AIChatTab(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the AI Chat tab UI"""
        self.layout = QVBoxLayout()
        
        # Chat history display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.layout.addWidget(self.input_field)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)
        
        self.setLayout(self.layout)
        self.logger.info("AI Chat tab initialized successfully")

    def send_message(self):
        """Handle sending of messages"""
# The line `if message := self.input_field.text():` is using the walrus operator `:=` introduced in
# Python 3.8.
        if message := self.input_field.text():
            self.chat_display.append(f"You: {message}")
            self.input_field.clear()
            self.logger.debug(f"Message sent: {message}")
