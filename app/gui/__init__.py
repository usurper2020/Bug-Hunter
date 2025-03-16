"""
GUI module initialization file
"""

from .tabs.ai_chat_tab import AIChatTab
from .tabs.analytics_tab import AnalyticsTab
from .tabs.collaboration_tab import CollaborationTab
from .tabs.code_analysis_tab import CodeAnalysisTab
from .tabs.nuclei_tab import NucleiTab
from .tabs.report_tab import ReportTab
from .tabs.security_tab import SecurityTab
from .tabs.settings_tab import SettingsTab
from .tabs.tool_manager_tab import ToolManagerTab

__all__ = [
    'AIChatTab',
    'AnalyticsTab',
    'CollaborationTab',
    'CodeAnalysisTab',
    'NucleiTab',
    'ReportTab',
    'SecurityTab',
    'SettingsTab',
    'ToolManagerTab'
]
