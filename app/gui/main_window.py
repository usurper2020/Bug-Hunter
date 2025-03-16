from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMenuBar, QMessageBox, QStatusBar, QTabWidget
from PyQt6.QtGui import QAction
from app.gui.tabs import (
    AIChatTab, AIChatbotTab, AITab, AmassTab, AnalyticsTab, BaseTab,
    BugBountyTargetTab, CodeAnalysisTab, CollaborationTab, NucleiTab,
    ReportGeneratorTab, ScannerTab, ScopeTab, SettingsTab, ShodanTab,
    TargetsTab, ToolManagerTab, ToolTab, ToolsManagerTab, ToolsTab,
    VulnerabilityTab, WaybackTab
)
from app.config.config_manager import ConfigManager
from app.db.database_manager import DatabaseManager
from app.security.security_service import SecurityService
from app.logging.log_manager import LogManager

class MainWindow(QMainWindow):
    def __init__(self, config_manager: ConfigManager, db_manager: DatabaseManager, security_service: SecurityService, ai_service: AIService):
        super().__init__()
        self.logger = LogManager.get_logger("MainWindow")
        self.logger.info("Initializing MainWindow...")
        
        # Initialize components
        self.config_manager = config_manager
        self.db_manager = db_manager
        self.security_service = security_service
        self.ai_service = ai_service
        
        # Setup window
        self.setWindowTitle("BugHunter")
        self.setGeometry(100, 100, 1200, 800)
        
        # Load theme
        self.theme = Theme(self.config_manager)
        self.theme.apply_theme(self)
        
        # Initialize UI components
        self.init_ui()
        self.connect_signals()
        
        self.logger.info("MainWindow initialized successfully.")

    def init_ui(self):
        try:
            # Create main tab widget
            self.tab_widget = QTabWidget()
            self.setCentralWidget(self.tab_widget)

            # Initialize and add all tabs
            self.tool_manager_tab = ToolManagerTab(self.config_manager)
            self.scanner_tab = ScannerTab(self.config_manager, self.db_manager)
            self.report_tab = ReportGeneratorTab(self.db_manager)
            self.scope_tab = ScopeTab(self.config_manager)
            self.shodan_tab = ShodanTab(self.config_manager)
            self.wayback_tab = WaybackTab(self.config_manager)
            self.ai_chat_tab = AIChatTab(self.config_manager)
            self.ai_chatbot_tab = AIChatbotTab(self.config_manager)
            self.ai_tab = AITab(self.config_manager)
            self.amass_tab = AmassTab(self.config_manager)
            self.analytics_tab = AnalyticsTab(self.config_manager)
            self.base_tab = BaseTab(self.config_manager)
            self.bug_bounty_target_tab = BugBountyTargetTab(self.config_manager)
            self.code_analysis_tab = CodeAnalysisTab(self.config_manager)
            self.collaboration_tab = CollaborationTab(self.config_manager)
            self.nuclei_tab = NucleiTab(self.config_manager)
            self.settings_tab = SettingsTab(self.config_manager)
            self.targets_tab = TargetsTab(self.config_manager)
            self.tool_tab = ToolTab(self.config_manager)
            self.tools_manager_tab = ToolsManagerTab(self.config_manager)
            self.tools_tab = ToolsTab(self.config_manager)
            self.vulnerability_tab = VulnerabilityTab(self.config_manager)

            # Add tabs to the tab widget
            self.tab_widget.addTab(self.tool_manager_tab, "Tool Manager")
            self.tab_widget.addTab(self.scanner_tab, "Scanner")
            self.tab_widget.addTab(self.report_tab, "Reports")
            self.tab_widget.addTab(self.scope_tab, "Scope Management")
            self.tab_widget.addTab(self.shodan_tab, "Shodan")
            self.tab_widget.addTab(self.wayback_tab, "Wayback Machine")
            self.tab_widget.addTab(self.ai_chat_tab, "AI Chat")
            self.tab_widget.addTab(self.ai_chatbot_tab, "AI Chatbot")
            self.tab_widget.addTab(self.ai_tab, "AI")
            self.tab_widget.addTab(self.amass_tab, "Amass")
            self.tab_widget.addTab(self.analytics_tab, "Analytics")
            self.tab_widget.addTab(self.base_tab, "Base")
            self.tab_widget.addTab(self.bug_bounty_target_tab, "Bug Bounty Targets")
            self.tab_widget.addTab(self.code_analysis_tab, "Code Analysis")
            self.tab_widget.addTab(self.collaboration_tab, "Collaboration")
            self.tab_widget.addTab(self.nuclei_tab, "Nuclei")
            self.tab_widget.addTab(self.settings_tab, "Settings")
            self.tab_widget.addTab(self.targets_tab, "Targets")
            self.tab_widget.addTab(self.tool_tab, "Tool")
            self.tab_widget.addTab(self.tools_manager_tab, "Tools Manager")
            self.tab_widget.addTab(self.tools_tab, "Tools")
            self.tab_widget.addTab(self.vulnerability_tab, "Vulnerability")

            # Initialize status bar
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)

            # Initialize menu bar
            self.menu_bar = QMenuBar()
            self.setMenuBar(self.menu_bar)
            self.init_menu()
            
        except Exception as e:
            self.logger.error(f"UI initialization error: {e}")
            self.show_error_message("Initialization Error", f"Failed to initialize UI components: {str(e)}")

    def init_menu(self):
        try:
            # Create menu items
            file_menu = self.menu_bar.addMenu("File")
            edit_menu = self.menu_bar.addMenu("Edit")
            view_menu = self.menu_bar.addMenu("View")
            help_menu = self.menu_bar.addMenu("Help")

            # File menu actions
            open_action = QAction("Open", self)
            open_action.triggered.connect(self.open_file)
            file_menu.addAction(open_action)

            save_action = QAction("Save", self)
            save_action.triggered.connect(self.save_file)
            file_menu.addAction(save_action)

            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # Edit menu actions
            undo_action = QAction("Undo", self)
            edit_menu.addAction(undo_action)

            redo_action = QAction("Redo", self)
            edit_menu.addAction(redo_action)

            # View menu actions
            toggle_status_bar_action = QAction("Toggle Status Bar", self)
            toggle_status_bar_action.setCheckable(True)
            toggle_status_bar_action.setChecked(True)
            toggle_status_bar_action.triggered.connect(self.toggle_status_bar)
            view_menu.addAction(toggle_status_bar_action)

            # Help menu actions
            about_action = QAction("About", self)
            about_action.triggered.connect(self.show_about_dialog)
            help_menu.addAction(about_action)
            
        except Exception as e:
            self.logger.error(f"Menu initialization error: {e}")
            self.show_error_message("Menu Initialization Error", f"Failed to initialize menu: {str(e)}")

    def connect_signals(self):
        try:
            # Connect tool manager signals
            self.tool_manager_tab.tool_installed.connect(self.scanner_tab.update_tools_list)
            self.tool_manager_tab.tool_removed.connect(self.scanner_tab.update_tools_list)

            # Connect scanner signals
            self.scanner_tab.scan_complete.connect(self.report_tab.add_scan_result)
            self.scanner_tab.status_message.connect(self.status_bar.showMessage)

            # Connect scope management signals
            self.scope_tab.scope_updated.connect(self.scanner_tab.update_scan_scope)
            self.scope_tab.status_message.connect(self.status_bar.showMessage)

            # Connect report generator signals
            self.report_tab.report_generated.connect(self.status_bar.showMessage)
            
        except Exception as e:
            self.logger.error(f"Signal connection error: {e}")
            self.show_error_message("Signal Connection Error", f"Failed to connect signals: {str(e)}")

    def open_file(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
            if file_name:
                self.status_bar.showMessage(f"Opened file: {file_name}")
        except Exception as e:
            self.logger.error(f"File open error: {e}")
            self.show_error_message("File Open Error", f"Failed to open file: {str(e)}")

    def save_file(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save File", "", "All Files (*);;Text Files (*.txt)", options=options)
            if file_name:
                self.status_bar.showMessage(f"Saved file: {file_name}")
        except Exception as e:
            self.logger.error(f"File save error: {e}")
            self.show_error_message("File Save Error", f"Failed to save file: {str(e)}")

    def toggle_status_bar(self, state):
        try:
            self.status_bar.setVisible(state)
        except Exception as e:
            self.logger.error(f"Status bar toggle error: {e}")
            self.show_error_message("Status Bar Toggle Error", f"Failed to toggle status bar: {str(e)}")

    def show_about_dialog(self):
        try:
            QMessageBox.about(self, "About BugHunter", 
                "BugHunter Version 2.0.0\nDeveloped by BugHunter Team")
        except Exception as e:
            self.logger.error(f"About dialog error: {e}")
            self.show_error_message("About Dialog Error", f"Failed to show about dialog: {str(e)}")

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)
