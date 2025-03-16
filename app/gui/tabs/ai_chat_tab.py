from PyQt5.QtWidgets import QVBoxLayout, QTextEdit, QLineEdit
from app.gui.base_tab import BaseTab

class AIChatTab(BaseTab):
    def __init__(self, managers, parent=None):
        super().__init__(managers, "AI Chat", parent)
        self.ai_service = managers.ai
        self._setup_ui()

    def _setup_ui(self):
        """Setup the AI chat interface"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self._process_input)
        self.layout.addWidget(self.input_field)

    def _process_input(self):
        """Process user input and display AI response"""
        if user_input := self.input_field.text():
            self.chat_display.append(f"You: {user_input}")
            try:
                response = self.ai_service.process_input(user_input)
                self.chat_display.append(f"AI: {response}")
            except Exception as e:
                self.chat_display.append(f"Error: {str(e)}")
            finally:
                self.input_field.clear()

    def cleanup(self):
        """Clean up resources"""
        super().cleanup()
        # Additional cleanup if needed