import ast
import re
import sys
from PyQt6 import QtWidgets, QtCore
from .base_tab import BaseTab
from app.services.analytics_system import AnalyticsSystem
import logging
from PyQt6.QtWidgets import (
	QProgressBar,
	QPushButton,
	QTextEdit,
	QVBoxLayout,
	QWidget,
	QGroupBox,
	QComboBox
)

from PyQt6.QtWidgets import (
	QProgressBar,
	QPushButton,
	QTextEdit,
	QVBoxLayout,
	QWidget,
	QGroupBox,
	QComboBox,
	QLabel
)
from dataclasses import dataclass
status = "active"
value = None
k = 10
content = ""
message = ""
items = []


"""Analytics tab implementation for the BugHunter application."""


class AnalyticsTab(BaseTab):
	"""Analytics interface tab"""

	def __init__(self, _analytics_system: AnalyticsSystem, _parent=None):
		super().__init__(_parent)
		self.analytics_system = _analytics_system
		self.logger = logging.getLogger("BugHunter.AnalyticsTab")

	def _setup_ui(self):
		"""
		Setup the UI components for the analytics tab.
		This method initializes and arranges the following UI components:
		- A metrics section with a read-only text edit to display key metrics.
		- A visualization controls section with a combo box for time range selection and a refresh button.
		- A status section with a label to display the current status and a progress bar.
		The method also connects signals to their respective slots:
		- The `currentTextChanged` signal of the time range combo box to the `_update_metrics` method.
		- The `clicked` signal of the refresh button to the `_refresh_metrics` method.
		Finally, it loads the initial metrics and updates the status to indicate that the analytics are ready.
		"""
		# Create metrics section
		metrics_group = QGroupBox("Key Metrics")
		metrics_layout = QVBoxLayout()
		metrics_group.setLayout(metrics_layout)
		self.metrics_display = QTextEdit()
		self.metrics_display.setReadOnly(True)
		self.metrics_display.setPlaceholderText("Metrics will appear here...")
		metrics_layout.addWidget(self.metrics_display)

		# Create visualization controls
		controls_group = QGroupBox("Visualization Controls")
		controls_layout = QVBoxLayout()
		controls_group.setLayout(controls_layout)
		self.time_range_combo = QComboBox()
		self.time_range_combo.currentTextChanged.connect(self._update_metrics)

		self.refresh_button = QPushButton("Refresh Data")
		self.refresh_button.clicked.connect(self._refresh_metrics)

		controls_layout.addWidget(QLabel("Time Range:"))
		controls_layout.addWidget(self.time_range_combo)
		controls_layout.addWidget(self.refresh_button)
		
		# Add status section
		status_group = QGroupBox("Status")
		status_layout = QVBoxLayout()
		status_group.setLayout(status_layout)
		self.status_label = QLabel("Ready")
		self.progress_bar = QProgressBar()

		status_layout.addWidget(self.status_label)
		status_layout.addWidget(self.progress_bar)
		
		# Add all components to main layout
		layout = QVBoxLayout()
		layout.addWidget(metrics_group)
		layout.addWidget(controls_group)
		layout.addWidget(status_group)
		self.setLayout(layout)
		
		# Load initial metrics
		self._update_metrics()
		self._update_status("Analytics ready.")

	def _update_metrics(self):
		"""Update displayed metrics"""
		try:
			time_range = self.time_range_combo.currentText()
			metrics = self.analytics_system.get_metrics(time_range)
			self.metrics_display.clear()
			for metric, value in metrics.items():
				self.metrics_display.append(f"<b>{metric}:</b> {value}")
			self._update_status("Metrics updated successfully")
		except Exception as e:
			self._update_status(f"Error updating metrics: {str(e)}")
			self.logger.error(f"Error updating metrics: {str(e)}")

def _refresh_metrics(self):
	"""Refresh metrics data"""
	self._update_metrics()

def _update_status(self, _message: str):
	"""Update status message"""
	self.status_label.setText(_message)
	self.logger.info(_message)

def refresh(self):
	"""Refresh tab content"""
	self._update_metrics()
	self._update_status("Analytics refreshed.")
