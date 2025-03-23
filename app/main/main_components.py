from app.ai.ai_tab import AITab
from app.settings.settings_tab import SettingsTab
from app.tools.tools_tab import ToolsTab
from app.scanners.scanners_tab import ScannersTab

class MainComponents:
    def __init__(self, managers):
        self.managers = managers
        self.tabs = {
            "AI": AITab(self.managers),
            "Settings": SettingsTab(self.managers),
            "Tools": ToolsTab(self.managers),
            "Scanners": ScannersTab(self.managers),
        }

    def get_tabs(self):
        return self.tabs
