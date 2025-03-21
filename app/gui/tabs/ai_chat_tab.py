from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (
    QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QMenu, QMessageBox, QFileDialog, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from app.gui.base_tab import BaseTab
import json
from datetime import datetime

class AIChatTab(BaseTab):
    def __init__(self, managers, parent=None):
        super().__init__(managers, "AI Chat", parent)
        self.ai_service = managers.ai
        self.chat_history = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the AI chat interface"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._setup_chat_display()
        self._setup_input_field()
        self._setup_buttons()
        self._setup_context_menu()

    def _setup_chat_display(self):
        """Setup the chat display area"""
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

    def _setup_input_field(self):
        """Setup the input field"""
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self._process_input)
        self.layout.addWidget(self.input_field)

    def _setup_buttons(self):
        """Setup the buttons for saving and clearing chat"""
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Chat")
        self.save_button.clicked.connect(self.save_chat)
        button_layout.addWidget(self.save_button)

        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)

        self.layout.addLayout(button_layout)

    def _setup_context_menu(self):
        """Setup the context menu for chat display"""
        self.chat_display.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.chat_display.customContextMenuRequested.connect(self.show_context_menu)

    def _process_input(self):
        """Process user input and display AI response"""
        if user_input := self.input_field.text().strip():
            self._append_message("You", user_input)
            self.input_field.clear()
            self._get_ai_response(user_input)

    def _get_ai_response(self, user_input):
        """Get AI response and update chat display"""
        try:
            response = self.ai_service.process_input(user_input)
            self._append_message("AI", response)
        except Exception as e:
            self._append_message("Error", str(e))

    def _append_message(self, sender, message):
        """Append a message to the chat display and history"""
        self.chat_display.append(f"{sender}: {message}")
        self.chat_history.append({"sender": sender, "message": message, "timestamp": datetime.now()})

    def save_chat(self):
        """Save the chat history to a file"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Chat History", "", "JSON Files (*.json);;Text Files (*.txt)", options=options)
        if file_path:
            self._write_chat_to_file(file_path)

    def _write_chat_to_file(self, file_path):
        """Write the chat history to a file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.chat_history, f, default=str)
            QMessageBox.information(self, "Success", "Chat history saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save chat history: {str(e)}")

    def clear_chat(self):
        """Clear the chat display and history"""
        self.chat_display.clear()
        self.chat_history.clear()

    def show_context_menu(self, position):
        """Show context menu for chat display"""
        menu = QMenu(self)
        copy_action = menu.addAction("Copy Message")
        action = menu.exec_(self.chat_display.mapToGlobal(position))
        if action == copy_action:
            self._copy_selected_text()

    def _copy_selected_text(self):
        """Copy the selected text to the clipboard"""
        cursor = self.chat_display.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        if selected_text := cursor.selectedText():
            clipboard = QtWidgets.QApplication.instance().clipboard()
            clipboard.setText(selected_text)

    def cleanup(self):
        """Clean up resources"""
        super().cleanup()
        # Additional cleanup if needed