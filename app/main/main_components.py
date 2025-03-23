import logging
from app.gui.tabs.ai_chatbot_tab import AIChatbotTab
from app.gui.tabs.analytics_tab import AnalyticsTab
from app.gui.tabs.collaboration_tab import CollaborationTab
from app.gui.tabs.code_analysis_tab import CodeAnalysisTab
from app.gui.tabs.nuclei_tab import NucleiTab
from app.gui.tabs.report_generator_tab import ReportGeneratorTab
from app.gui.tabs.security_tab import SecurityTab
from app.gui.tabs.settings_tab import SettingsTab
from app.gui.tabs.tool_manager_tab import ToolManagerTab

logger = logging.getLogger(__name__)


class MainComponents:
    def __init__(self, managers):
        self.managers = managers
        self.tabs = {}

    def initialize_components(self):
        try:
            # Initialize each tab component
            self.tabs["AI Chatbot"] = AIChatbotTab(self.managers.config)
            self.tabs["Analytics"] = AnalyticsTab(self.managers.config)
            self.tabs["Collaboration"] = CollaborationTab(self.managers.config)
            self.tabs["Code Analysis"] = CodeAnalysisTab(self.managers.config)
            self.tabs["Nuclei"] = NucleiTab(self.managers.config)
            self.tabs["Report Generator"] = ReportGeneratorTab(self.managers.config)
            self.tabs["Security"] = SecurityTab(self.managers.config)
            self.tabs["Settings"] = SettingsTab(self.managers.config)
            self.tabs["Tool Manager"] = ToolManagerTab(self.managers.config)

            logger.info("All components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {str(e)}")
            raise

    def add_tabs_to_main_window(self, main_window):
        try:
            for tab_name, tab in self.tabs.items():
                main_window.tab_widget.addTab(tab, tab_name)
            logger.info("All tabs added to main window successfully")
        except Exception as e:
            logger.error(f"Failed to add tabs to main window: {str(e)}")
            raise
            raise
