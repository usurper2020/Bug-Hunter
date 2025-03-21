import json
import os
from typing import List, Dict, Any
from datetime import datetime

class CollaborationSystem:
    def __init__(self):
        self.online_users = set()  # Set to track online users
        self.messages = []          # List to store chat messages
        self.tasks = []             # List to store tasks
        self.projects = []          # List to store projects
        self.data_dir = os.path.join("data", "collaboration")
        self.ensure_directories()
        self.load_data()

    def ensure_directories(self):
        """Ensure required directories exist."""
        os.makedirs(self.data_dir, exist_ok=True)

    def load_data(self):
        """Load messages, tasks, and projects from files."""
        self.load_messages()
        self.load_tasks()
        self.load_projects()

    def load_messages(self):
        """Load messages from a JSON file."""
        try:
            with open(os.path.join(self.data_dir, 'messages.json'), 'r') as f:
                self.messages = json.load(f)
        except FileNotFoundError:
            self.messages = []

    def load_tasks(self):
        """Load tasks from a JSON file."""
        try:
            with open(os.path.join(self.data_dir, 'tasks.json'), 'r') as f:
                self.tasks = json.load(f)
        except FileNotFoundError:
            self.tasks = []

    def load_projects(self):
        """Load projects from a JSON file."""
        try:
            with open(os.path.join(self.data_dir, 'projects.json'), 'r') as f:
                self.projects = json.load(f)
        except FileNotFoundError:
            self.projects = []

    def save_data(self):
        """Save messages, tasks, and projects to files."""
        self.save_messages()
        self.save_tasks()
        self.save_projects()

    def save_messages(self):
        """Save messages to a JSON file."""
        with open(os.path.join(self.data_dir, 'messages.json'), 'w') as f:
            json.dump(self.messages, f)

    def save_tasks(self):
        """Save tasks to a JSON file."""
        with open(os.path.join(self.data_dir, 'tasks.json'), 'w') as f:
            json.dump(self.tasks, f)

    def save_projects(self):
        """Save projects to a JSON file."""
        with open(os.path.join(self.data_dir, 'projects.json'), 'w') as f:
            json.dump(self.projects, f)

    def send_message(self, sender: str, content: str):
        """Send a chat message and store it in the message history."""
        message = {
            "sender": sender,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)
        self.save_messages()  # Save messages after sending

    def add_task(self, task: str, assigned_to: str = None):
        """Add a new task to the task list."""
        task_entry = {
            "task": task,
            "assigned_to": assigned_to,
            "completed": False
        }
        self.tasks.append(task_entry)
        self.save_tasks()  # Save tasks after adding

    def complete_task(self, task_index: int):
        """Mark a task as completed."""
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]["completed"] = True
            self.save_tasks()  # Save tasks after completing

    def get_online_users(self) -> List[str]:
        """Return a list of online users."""
        return list(self.online_users)

    def get_messages(self) -> List[Dict[str, Any]]:
        """Return the list of chat messages."""
        return self.messages

    def get_tasks(self) -> List[Dict[str, Any]]:
        """Return the list of tasks."""
        return self.tasks

    def get_projects(self) -> List[Dict[str, Any]]:
        """Return the list of projects."""
        return self.projects

    def create_project(self, name: str, description: str, creator: str) -> Dict[str, Any]:
        """Create a new project."""
        project = {
            "id": len(self.projects) + 1,
            "name": name,
            "description": description,
            "creator": creator,
            "members": []
        }
        self.projects.append(project)
        self.save_projects()  # Save projects after creating
        return {"status": "success", "project": project}

    def delete_project(self, project_name: str) -> Dict[str, str]:
        """Delete a project by name."""
        for project in self.projects:
            if project["name"] == project_name:
                self.projects.remove(project)
                self.save_projects()  # Save projects after deletion
                return {"status": "success", "message": "Project deleted."}
        return {"status": "error", "message": "Project not found."}

    def user_joined(self, username: str):
        """Add a user to the online users list."""
        self.online_users.add(username)

    def user_left(self, username: str):
        """Remove a user from the online users list."""
        self.online_users.discard(username)

    def get_status(self) -> str:
        """Return a status message about the collaboration system."""
        return f"Online users: {len(self.online_users)}, Total messages: {len(self.messages)}, Total tasks: {len(self.tasks)}, Total projects: {len(self.projects)}"
class CollaborationSystem:
    def __init__(self):
        self.online_users = set()  # Set to track online users
        self.messages = []          # List to store chat messages
        self.tasks = []             # List to store tasks

    def send_message(self, message: str):
        """Send a chat message and store it in the message history."""
        self.messages.append(message)

    def add_task(self, task: str):
        """Add a new task to the task list."""
        self.tasks.append(task)

    def get_online_users(self):
        """Return a list of online users."""
        return list(self.online_users)

    def get_messages(self):
        """Return the list of chat messages."""
        return self.messages

    def get_tasks(self):
        """Return the list of tasks."""
        return self.tasks

    def get_status(self):
        """Return a status message about the collaboration system."""
        return f"Online users: {len(self.online_users)}, Total messages: {len(self.messages)}, Total tasks: {len(self.tasks)}"

    def user_joined(self, username: str):
        """Add a user to the online users list."""
        self.online_users.add(username)

    def user_left(self, username: str):
        """Remove a user from the online users list."""
        self.online_users.discard(username)
