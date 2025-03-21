import re
import sys
import time
import json
import os
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import (
    QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout,
    QSplitter, QWidget, QScrollArea, QFrame, QMenu, QFileDialog,
    QProgressBar, QMessageBox, QComboBox, QCheckBox, QToolButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QColor, QTextCursor, QFont, QIcon

from app.gui.tabs.base_tab import BaseTab
from app.ai.ai_service import AIService

class ChatMessage:
    """Class representing a chat message."""
    
    def __init__(self, content: str, is_user: bool, timestamp: Optional[datetime] = None):
        self.content = content
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "content": self.content,
            "is_user": self.is_user,
            "timestamp": self.timestamp.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create message from dictionary."""
        return cls(
            content=data["content"],
            is_user=data["is_user"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class ChatSession:
    """Class representing a chat session with history."""
    
    def __init__(self, title: str = "New Chat"):
        self.title = title
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def add_message(self, content: str, is_user: bool) -> ChatMessage:
        """Add a message to the chat history."""
        message = ChatMessage(content, is_user)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
        
    def clear(self) -> None:
        """Clear all messages from the session."""
        self.messages.clear()
        self.updated_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create session from dictionary."""
        session = cls(title=data["title"])
        session.messages = [ChatMessage.from_dict(msg) for msg in data["messages"]]
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.updated_at = datetime.fromisoformat(data["updated_at"])
        return session


class AIResponseWorker(QThread):
    """Worker thread for getting AI responses without blocking the UI."""
    
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ai_service: AIService, message: str):
        super().__init__()
        self.ai_service = ai_service
        self.message = message
        
    def run(self):
        """Run the AI processing in a separate thread."""
        try:
            response = self.ai_service.process_input(self.message)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MessageWidget(QFrame):
    """Widget for displaying a single chat message."""
    
    def __init__(self, message: ChatMessage, parent=None):
        super().__init__(parent)
        self.message = message
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the message widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Header with timestamp and sender
        header_layout = QHBoxLayout()
        
        sender = "You" if self.message.is_user else "AI Assistant"
        sender_label = QLabel(f"<b>{sender}</b>")
        header_layout.addWidget(sender_label)
        
        timestamp = self.message.timestamp.strftime("%H:%M:%S")
        time_label = QLabel(timestamp)
        time_label.setStyleSheet("color: gray;")
        header_layout.addWidget(time_label, 0, Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(header_layout)
        
        # Message content
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self._format_message(self.message.content))
        content.setFrameStyle(QFrame.Shape.NoFrame)
        content.setStyleSheet(
            "background-color: transparent; border: none;"
        )
        
        # Adjust height to content
        document_height = content.document().size().height()
        content.setFixedHeight(int(document_height) + 20)
        
        layout.addWidget(content)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        copy_btn = QToolButton()
        copy_btn.setText("Copy")
        copy_btn.setToolTip("Copy message to clipboard")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        actions_layout.addWidget(copy_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Set frame style based on sender
        if self.message.is_user:
            self.setStyleSheet(
                "MessageWidget { background-color: #e1f5fe; border-radius: 5px; }"
            )
        else:
            self.setStyleSheet(
                "MessageWidget { background-color: #f5f5f5; border-radius: 5px; }"
            )
            
    def _format_message(self, content: str) -> str:
        """Format the message content with HTML."""
        # Convert URLs to clickable links
        url_pattern = r'https?://[^\s]+'
        content = re.sub(url_pattern, r'<a href="\g<0>">\g<0></a>', content)
        
        # Format code blocks
        code_pattern = r'```(.*?)```'
        content = re.sub(code_pattern, r'<pre style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">\1</pre>', content, flags=re.DOTALL)
        
        # Format inline code
        inline_code_pattern = r'`(.*?)`'
        content = re.sub(inline_code_pattern, r'<code style="background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px;">\1</code>', content)
        
        return content
        
    def copy_to_clipboard(self):
        """Copy the message content to clipboard."""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.message.content)


class AIChatbotTab(BaseTab):
    """
    Enhanced tab widget providing AI chatbot functionality.

    Features:
    - Interactive chat interface with conversation history
    - Security-focused AI responses
    - Session management (save/load/clear)
    - Message formatting with code highlighting
    - Copy functionality for messages
    - Loading indicator for AI responses
    """

    def __init__(self, config_manager):
        """
        Initialize the AI chatbot interface.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.tab_name = "AI Chatbot"
        super().__init__(config_manager)
        
        # Initialize AI service
        self.ai_service = AIService()
        self.logger = logging.getLogger(__name__)
        self.ai_service.initialize()
        
        # Initialize chat session
        self.current_session = ChatSession()
        self.sessions_dir = os.path.join(
            self.config_manager.get_data_dir(), 
            "chat_sessions"
        )
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Initialize worker
        self.response_worker = None
        
    def _setup_ui(self):
        """Set up the UI components specific to this tab."""
        # Create main layout with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Sessions
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Session management
        session_header = QHBoxLayout()
        session_header.addWidget(QLabel("<b>Chat Sessions</b>"))
        
        new_session_btn = QPushButton("New")
        new_session_btn.clicked.connect(self.new_session)
        session_header.addWidget(new_session_btn)
        
        left_layout.addLayout(session_header)
        
        # Sessions list
        self.sessions_list = QtWidgets.QListWidget()
        self.sessions_list.itemClicked.connect(self.load_session)
        self.sessions_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sessions_list.customContextMenuRequested.connect(self.show_session_context_menu)
        left_layout.addWidget(self.sessions_list)
        
        # Right panel - Chat interface
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Chat title and controls
        title_layout = QHBoxLayout()
        self.chat_title = QLabel("<b>New Chat</b>")
        title_layout.addWidget(self.chat_title)
        
        # Chat controls
        self.clear_chat_btn = QPushButton("Clear Chat")
        self.clear_chat_btn.clicked.connect(self.clear_chat)
        title_layout.addWidget(self.clear_chat_btn)
        
        self.save_chat_btn = QPushButton("Save Chat")
        self.save_chat_btn.clicked.connect(self.save_session)
        title_layout.addWidget(self.save_chat_btn)
        
        right_layout.addLayout(title_layout)
        
        # Chat messages area
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()
        
        self.chat_scroll_area.setWidget(self.chat_container)
        right_layout.addWidget(self.chat_scroll_area)
        
        # Input area
        input_layout = QVBoxLayout()
        
        # AI mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("AI Mode:"))
        
        self.ai_mode = QComboBox()
        self.ai_mode.addItems(["Security Expert", "Vulnerability Analyst", "Code Reviewer", "General Assistant"])
        mode_layout.addWidget(self.ai_mode)
        
        self.technical_mode = QCheckBox("Technical Mode")
        self.technical_mode.setToolTip("Include technical details in responses")
        mode_layout.addWidget(self.technical_mode)
        
        input_layout.addLayout(mode_layout)
        
        # Message input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setMaximumHeight(100)
        input_layout.addWidget(self.message_input)
        
        # Send button and progress
        send_layout = QHBoxLayout()
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        send_layout.addWidget(self.send_button)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        send_layout.addWidget(self.progress_bar)
        
        input_layout.addLayout(send_layout)
        right_layout.addLayout(input_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([300, 700])
        
        # Add splitter to main layout
        self.add_widget(splitter)
        
        # Load existing sessions
        self.load_sessions_list()
        
    def connect_signals(self):
        """Connect signals for this tab."""
        self.message_input.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        """Handle events for filtered objects."""
        if obj == self.message_input and event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return:
                if event.modifiers() == Qt.KeyboardModifier.NoModifier:
                    self.send_message()
                    return True
                elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                    # Allow Shift+Enter for new line
                    return False
        return super().eventFilter(obj, event)
        
    def send_message(self):
        """Process and send user message to AI system."""
        user_message = self.message_input.toPlainText().strip()
        if not user_message:
            return
            
        # Add user message to chat
        self.add_message_to_chat(user_message, True)
        self.message_input.clear()
        
        # Show progress indicator
        self.progress_bar.setVisible(True)
        self.send_button.setEnabled(False)
        
        # Prepare context for AI
        ai_mode = self.ai_mode.currentText()
        technical = self.technical_mode.isChecked()
        
        # Prepare the full message with context
        context_message = f"[Mode: {ai_mode}, Technical: {'Yes' if technical else 'No'}]\n{user_message}"
        
        # Get AI response in a separate thread
        self.response_worker = AIResponseWorker(self.ai_service, context_message)
        self.response_worker.response_ready.connect(self.handle_ai_response)
        self.response_worker.error_occurred.connect(self.handle_ai_error)
        self.response_worker.start()
        
    def handle_ai_response(self, response):
        """Handle the AI response."""
        # Hide progress indicator
        self.progress_bar.setVisible(False)
        self.send_button.setEnabled(True)
        
        # Add AI response to chat
        self.add_message_to_chat(response, False)
        
    def handle_ai_error(self, error_message):
        """Handle errors from the AI service."""
        # Hide progress indicator
        self.progress_bar.setVisible(False)
        self.send_button.setEnabled(True)
        
        # Add error message to chat
        error_text = f"Error: {error_message}\n\nPlease try again or check the AI service configuration."
        self.add_message_to_chat(error_text, False)
        
    def add_message_to_chat(self, content, is_user):
        """Add a message to the chat display."""
        # Add to session
        message = self.current_session.add_message(content, is_user)
        
        # Create and add message widget
        message_widget = MessageWidget(message)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_widget)
        
        # Scroll to bottom
        QtCore.QTimer.singleShot(100, self.scroll_to_bottom)
        
    def scroll_to_bottom(self):
        """Scroll the chat area to the bottom."""
        scrollbar = self.chat_scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_chat(self):
        """Clear the current chat session."""
        reply = QMessageBox.question(
            self, "Clear Chat",
            "Are you sure you want to clear the current chat?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear session
            self.current_session.clear()
            
            # Clear UI
            self._clear_chat_layout()
            
    def _clear_chat_layout(self):
        """Clear the chat layout."""
        # Remove all widgets except the stretch at the end
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def new_session(self):
        """Create a new chat session."""
        self.current_session = ChatSession()
        self.chat_title.setText("<b>New Chat</b>")
        self._clear_chat_layout()
        
    def save_session(self):
        """Save the current session."""
        if not self.current_session.messages:
            self.show_message("No Messages", "There are no messages to save.")
            return
            
        # Ask for session title if it's a new session
        if self.current_session.title == "New Chat":
            title, ok = QtWidgets.QInputDialog.getText(
                self, "Save Chat Session", "Enter a title for this chat session:"
            )
            if ok and title:
                self.current_session.title = title
            else:
                return
                
        # Save to file
        try:
            filepath = self._get_session_filepath()
            
            with open(filepath, 'w') as f:
                json.dump(self.current_session.to_dict(), f, indent=2)
                
            self.chat_title.setText(f"<b>{self.current_session.title}</b>")
            self.load_sessions_list()
            self.show_message("Session Saved", f"Chat session '{self.current_session.title}' saved successfully.")
            
        except Exception as e:
            self.show_error("Save Error", f"Failed to save session: {str(e)}")
            
    def load_sessions_list(self):
        """Load the list of saved chat sessions."""
        self.sessions_list.clear()

        try:
            session_files = [f for f in os.listdir(self.sessions_dir) if f.endswith('.json')]
            session_files.sort(reverse=True)  # Most recent first

            for filename in session_files:
                filepath = os.path.join(self.sessions_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        title = data.get("title", "Untitled")
                        created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
                        date_str = created_at.strftime("%Y-%m-%d %H:%M")

                        item = QtWidgets.QListWidgetItem(f"{title} ({date_str})")
                        item.setData(Qt.ItemDataRole.UserRole, filepath)
                        self.sessions_list.addItem(item)
                except Exception as e:
                    self.logger.error(f"Error loading session {filename}: {str(e)}")

        except Exception as e:
            self.show_error("Load Error", f"Failed to load sessions: {str(e)}")
            
    def _get_session_filepath(self):
        """Generate the file path for the current session."""
        filename = f"{self.current_session.created_at.strftime('%Y%m%d%H%M%S')}.json"
        return os.path.join(self.sessions_dir, filename)
        
            
    def load_session(self, item):
        """Load a selected session."""
        filepath = item.data(Qt.ItemDataRole.UserRole)
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.current_session = ChatSession.from_dict(data)
                
            # Update UI
            self.chat_title.setText(f"<b>{self.current_session.title}</b>")
            self._clear_chat_layout()
            
            # Add messages to chat
            for message in self.current_session.messages:
                message_widget = MessageWidget(message)
                self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_widget)
                
            # Scroll to bottom
            self.scroll_to_bottom()
            
        except Exception as e:
            self.show_error("Load Error", f"Failed to load session: {str(e)}")
            
    def show_session_context_menu(self, position):
        """Show context menu for sessions list."""
        item = self.sessions_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        load_action = menu.addAction("Load Session")
        rename_action = menu.addAction("Rename Session")
        delete_action = menu.addAction("Delete Session")
        export_action = menu.addAction("Export Session")
        
        action = menu.exec(self.sessions_list.mapToGlobal(position))
        
        filepath = item.data(Qt.ItemDataRole.UserRole)
        
        if action == load_action:
            self.load_session(item)
        elif action == rename_action:
            self.rename_session(filepath, item)
        elif action == delete_action:
            self.delete_session(filepath, item)
        elif action == export_action:
            self.export_session(filepath)
            
    def rename_session(self, filepath, item):
        """Rename a saved session."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            current_title = data.get("title", "Untitled")
            new_title, ok = QtWidgets.QInputDialog.getText(
                self, "Rename Session", "Enter new title:", 
                QtWidgets.QLineEdit.EchoMode.Normal, current_title
            )
            
            if ok and new_title:
                data["title"] = new_title
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                # Update list item
                created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
                date_str = created_at.strftime("%Y-%m-%d %H:%M")
                item.setText(f"{new_title} ({date_str})")
                
                # Update current session if it's the one being renamed
                if self.current_session.title == current_title:
                    self.current_session.title = new_title
                    self.chat_title.setText(f"<b>{new_title}</b>")
                    
        except Exception as e:
            self.show_error("Rename Error", f"Failed to rename session: {str(e)}")
            
    def delete_session(self, filepath, item):
        """Delete a saved session."""
        reply = QMessageBox.question(
            self, "Delete Session",
            "Are you sure you want to delete this session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(filepath)
                self.sessions_list.takeItem(self.sessions_list.row(item))
            except Exception as e:
                self.show_error("Delete Error", f"Failed to delete session: {str(e)}")
                
    def export_session(self, filepath):
        """Export a session to a file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            title = data.get("title", "chat_export")
            safe_title = re.sub(r'[^\w\-_]', '_', title)
            
            export_path, _ = QFileDialog.getSaveFileName(
                self, "Export Chat Session", 
                f"{safe_title}.txt",
                "Text Files (*.txt);;HTML Files (*.html);;JSON Files (*.json)"
            )
            
            if not export_path:
                return
                
            if export_path.endswith('.txt'):
                self._export_as_text(data, export_path)
            elif export_path.endswith('.html'):
                self._export_as_html(data, export_path)
            else:
                # Export as JSON (default)
                with open(export_path, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            self.show_message("Export Complete", f"Session exported to {export_path}")
            
        except Exception as e:
            self.show_error("Export Error", f"Failed to export session: {str(e)}")
            
    def _export_as_text(self, data, filepath):
        """Export session as plain text."""
        with open(filepath, 'w') as f:
            f.write(f"Chat Session: {data.get('title', 'Untitled')}\n")
            f.write(f"Date: {data.get('created_at', '')}\n\n")
            
            for msg in data.get('messages', []):
                sender = "You" if msg.get('is_user', False) else "AI"
                timestamp = datetime.fromisoformat(msg.get('timestamp', datetime.now().isoformat())).strftime("%H:%M:%S")
                f.write(f"[{timestamp}] {sender}:\n{msg.get('content', '')}\n\n")
                
    def _export_as_html(self, data, filepath):
        """Export session as HTML."""
        with open(filepath, 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Chat Session: {data.get('title', 'Untitled')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
        .message {{ padding: 10px; margin-bottom: 10px; border-radius: 5px; }}
        .user {{ background-color: #e1f5fe; }}
        .ai {{ background-color: #f5f5f5; }}
        .timestamp {{ color: gray; font-size: 0.8em; }}
        pre {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Chat Session: {data.get('title', 'Untitled')}</h1>
        <p>Date: {data.get('created_at', '')}</p>
    </div>
""")
            
            for msg in data.get('messages', []):
                sender = "You" if msg.get('is_user', False) else "AI Assistant"
                timestamp = datetime.fromisoformat(msg.get('timestamp', datetime.now().isoformat())).strftime("%H:%M:%S")
                content = msg.get('content', '')
                
                # Format code blocks
                content = re.sub(r'```(.*?)```', r'<pre>\1</pre>', content, flags=re.DOTALL)
                content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
                
                # Convert URLs to links
                content = re.sub(r'https?://[^\s]+', r'<a href="\g<0>">\g<0></a>', content)
                
                # Replace newlines with <br>
                content = content.replace('\n', '<br>')
                
                message_class = "user" if msg.get('is_user', False) else "ai"
                f.write(f"""
    <div class="message {message_class}">
        <div><strong>{sender}</strong> <span class="timestamp">{timestamp}</span></div>
        <div>{content}</div>
    </div>
""")
                
            f.write("""
</body>
</html>
""")
            
    def refresh(self):
        """Refresh the tab content."""
        self.load_sessions_list()
        
    def cleanup(self):
        """Clean up resources."""
        if self.response_worker and self.response_worker.isRunning():
            self.response_worker.terminate()
            self.response_worker.wait()
        self.ai_service.cleanup()
        super().cleanup()