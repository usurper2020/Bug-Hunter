from datetime import datetime
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget
)


class CollaborationDialog(QDialog):
    """
    Dialog for collaboration features.
    """

    message_sent = pyqtSignal(str)

    def __init__(self, collaboration_system, current_user, parent=None):
        """
        Initialize the CollaborationDialog.

        :param collaboration_system: The system managing collaboration features.
        :param current_user: The user currently using the dialog.
        :param parent: The parent widget, if any.
        """
        super().__init__(parent)
        self.collaboration_system = collaboration_system
        self.current_user = current_user
        self.current_project = None
        # The currently selected project in the dialog
        self.current_project = None

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        splitter.addWidget(self.setup_projects_ui())
        splitter.addWidget(self.setup_chat_ui())

    def setup_projects_ui(self):
        projects_widget = QWidget()
        projects_layout = QVBoxLayout()
        projects_widget.setLayout(projects_layout)

        projects_layout.addWidget(QLabel("Projects"))
        self.projects_list = QListWidget()
        self.load_projects()
        self.projects_list.itemSelectionChanged.connect(self.project_selected)
        self.projects_list.installEventFilter(self)

        self.project_name_input = QLineEdit()
        self.project_desc_input = QTextEdit()
        self.create_project_btn = QPushButton("Create Project")
        self.create_project_btn = QPushButton("Create Project")
        self.create_project_btn.clicked.connect(self.create_project)
        
        self.delete_project_btn = QPushButton("Delete Project")
        self.delete_project_btn.clicked.connect(self.delete_project)
        projects_layout.addWidget(QLabel("New Project Name"))
        projects_layout.addWidget(self.project_name_input)
        projects_layout.addWidget(QLabel("New Project Description"))
        projects_layout.addWidget(self.project_desc_input)
        projects_layout.addWidget(self.create_project_btn)

        projects_layout.addWidget(self.delete_project_btn)
        
        return projects_widget
    def load_projects(self):
        """
        Load the list of projects from the collaboration system and display them in the projects list widget.
        """
        self.projects_list.clear()
        projects = self.collaboration_system.get_projects()
        for project in projects:
            self.projects_list.addItem(project["name"])

    def setup_chat_ui(self):
        """
        Set up the UI components for the chat functionality.
    
        :return: The widget containing the chat UI.
        """
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        chat_widget.setLayout(chat_layout)

        self.chat_header = QLabel("No project selected")
        chat_layout.addWidget(self.chat_header)

        self.messages_display = QTextEdit()
        self.messages_display.setReadOnly(True)
        chat_layout.addWidget(self.messages_display)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        chat_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        chat_layout.addWidget(self.send_button)

        return chat_widget

    def delete_project(self):
        selected_item = self.projects_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Selection Error", "Please select a project to delete.")
            return

        project_name = selected_item.text()
        result = self.collaboration_system.delete_project(project_name=project_name)

        if result["status"] == "success":
            self.load_projects()
        else:
            QMessageBox.warning(self, "Error", "Failed to delete project.")

    def create_project(self):
        """
        Create a new project with the provided name and description.

        :return: None
        """
        name = self.project_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a project name.")
            return
        description = self.project_desc_input.toPlainText().strip()
        result = self.collaboration_system.create_project(
            name=name,
            description=description,
            creator=self.current_user
        )

        if result["status"] == "success":
            self.load_projects()
            self.project_name_input.clear()
            self.project_desc_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Failed to create project.")

    def send_message(self):
        """
        Send a message to the currently selected project.

        :return: None
        """
        message = self.message_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Input Error", "Please enter a message.")
            return
        if not self.current_project:
            QMessageBox.warning(self, "Error", "No project selected.")
            return
        result = self.collaboration_system.send_message(
            project_id=self.current_project["id"],
            sender=self.current_user,
            content=message
        )

        if result["status"] == "success":
            self.load_messages()
            self.message_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Failed to send message.")

    def project_selected(self, item):
        """
        Handle the event when a project is selected from the projects list.

        :param item: The selected project item.
        :return: None
        """
        project_name = item.text()
        self.current_project = self.collaboration_system.get_project_by_name(project_name)
        if self.current_project:
            self.chat_header.setText(f"Project: {self.current_project['name']}")
            self.load_messages()
        else:
            QMessageBox.warning(self, "Error", "Failed to load project details.")

    def load_messages(self):
        """
        Load and display messages for the current project.

        :return: None
        """
        try:
            result = self.collaboration_system.get_messages(project_id=self.current_project["id"])
            if result["status"] == "success":
                self.messages_display.clear()
                for message in result["messages"]:
                    timestamp = datetime.fromisoformat(message["timestamp"])
                    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    self.messages_display.append(f'[{formatted_time}] {message["sender"]}: {message["content"]}')
            else:
                QMessageBox.warning(self, "Error", "Failed to load messages.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading messages: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Failed to load messages.")
