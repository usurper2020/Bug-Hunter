from fpdf import FPDF
from collections import defaultdict
import json
import csv
import logging
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QFileDialog,
    QColorDialog,
    QComboBox,
)
from PyQt6.QtCore import pyqtSignal, QDate

logging.basicConfig(level=logging.INFO)

class PDFReport(FPDF):
    def __init__(self, template="Basic", title="", author="", date=""):
        super().__init__()
        self.template = template
        self.title = title
        self.author = author
        self.date = date
        self.colors = {
            "header": (0, 51, 102),
            "critical": (255, 0, 0),
            "high": (255, 128, 0),
            "medium": (255, 255, 0),
            "low": (0, 128, 0),
        }
        self.set_font("Arial", "", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"Author: {self.author} | Date: {self.date}", 0, 1, "C")
        self.ln(10)
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_executive_summary(self, findings):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Executive Summary", 0, 1)
        self.set_font("Arial", "", 12)

        severity_counts = defaultdict(int)
        for finding in findings:
            severity_counts[finding.get("severity", "Unknown")] += 1

        self.multi_cell(0, 10, f"This report summarizes the findings from the security scan conducted on {self.date}. The following key metrics were identified:")
        self.ln(5)

        for severity, count in severity_counts.items():
            self.cell(0, 10, f"- {severity} severity findings: {count}", 0, 1)

        self.ln(10)

    def add_recommendations(self, findings):
        self.add_section_title("Recommendations", font_size=14)
        self.set_font("Arial", "", 12)

        self.multi_cell(0, 10, 
            "Based on the findings, the following recommendations are proposed:\n"
            "1. Address critical and high severity findings immediately\n"
            "2. Review medium severity findings for potential risks\n"
            "3. Monitor low severity findings for future improvements\n"
            "4. Implement regular security audits\n"
            "5. Establish a vulnerability management process"
        )
        self.ln(10)

        severity_recommendations = {
            "Critical": "Immediate remediation required. These vulnerabilities pose the highest risk.",
            "High": "Prompt remediation recommended. These vulnerabilities could lead to significant impact.",
            "Medium": "Address based on risk assessment. These vulnerabilities may have moderate impact.",
        }

        self.add_severity_recommendations(severity_recommendations)
        self.add_section_title("Detailed Recommendations by Severity:", 12)
        self.set_font("Arial", "", 12)
        for severity, recommendation in severity_recommendations.items():
            self.cell(0, 10, f"{severity}: {recommendation}", 0, 1)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Recommendations", 0, 1)
        self.ln(5)

    def add_findings(self, findings):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Findings", 0, 1)
        self.set_font("Arial", "", 12)

        for finding in findings:
            severity = finding.get("severity", "").lower()
            color = self.colors.get(severity, (0, 0, 0))
            self.set_text_color(*color)

            self.cell(0, 10, f"Target: {finding.get('target', '')}", 0, 1)
            self.cell(0, 10, f"Vulnerability: {finding.get('vulnerability', '')}", 0, 1)
            self.cell(0, 10, f"Severity: {finding.get('severity', '')}", 0, 1)
            self.multi_cell(0, 10, f"Details: {finding.get('details', '')}")
            self.ln(5)
            self.set_text_color(0, 0, 0)

class ReportGeneratorTab(QWidget):
    report_generated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.title_input = None
        self.author_input = None
        self.scan_results = []
        self.init_ui()
        self.connect_signals()
        logging.info('Generating report')

    def init_ui(self):
        layout = QVBoxLayout()

        # Report metadata
        meta_layout = QHBoxLayout()
        self.title_input = self.add_meta_field(meta_layout, "Title:", "Enter report title")
        self.author_input = self.add_meta_field(meta_layout, "Author:", "Enter author name")
        layout.addLayout(meta_layout)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Target", "Vulnerability", "Severity", "Details"])
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.results_table)

        # Export controls
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("Export Format:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Basic", "Detailed", "Executive", "Technical"])
        export_layout.addWidget(self.template_combo)

        self.style_button = QPushButton("Customize Style")
        export_layout.addWidget(self.style_button)

        self.export_button = QPushButton("Export Report")
        export_layout.addWidget(self.export_button)

        layout.addLayout(export_layout)
        self.setLayout(layout)
        self.export_button.clicked.connect(self.export_report)

    def add_meta_field(self, layout, label_text, placeholder_text):
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        layout.addWidget(label)
        layout.addWidget(line_edit)
        return line_edit

    def add_scan_result(self, result):
        self.scan_results.append(result)
        self.update_results_table()

    def update_results_table(self):
        self.results_table.setRowCount(len(self.scan_results))

        for row, result in enumerate(self.scan_results):
            self.results_table.setItem(row, 0, QTableWidgetItem(result.get("target", "")))
            self.results_table.setItem(row, 1, QTableWidgetItem(result.get("vulnerability", "")))
            self.results_table.setItem(row, 2, QTableWidgetItem(result.get("severity", "")))
            self.results_table.setItem(row, 3, QTableWidgetItem(result.get("details", "")))

    def export_report(self):
        export_format = self.export_combo.currentText()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", f"{export_format} Files (*.{export_format.lower()})")

        if file_path:
            try:
                if export_format == "JSON":
                    self.export_json(file_path)
                elif export_format == "CSV":
                    self.export_csv(file_path)
                elif export_format == "PDF":
                    self.export_pdf(file_path)

                self.report_generated.emit(f"Report successfully exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export report: {str(e)}")

    def customize_style(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.apply_style(color)

    def apply_style(self, color):
        stylesheet = f"""
        QWidget {{
            background-color: {color.name()};
            color: #000000;
            font-family: Arial, sans-serif;
            font-size: 12pt;
        }}
        QTableWidget {{
            background-color: #FFFFFF;
            alternate-background-color: #F0F0F0;
        }}
        QHeaderView::section {{
            background-color: {color.name()};
            color: #FFFFFF;
            font-weight: bold;
        }}
        QPushButton {{
            background-color: {color.name()};
            color: #FFFFFF;
            border: 1px solid #000000;
            padding: 5px;
        }}
        """
        self.setStyleSheet(stylesheet)

    def export_json(self, file_path):
        report_data = {
            "title": self.title_input.text(),
            "author": self.author_input.text(),
            "date": QDate.currentDate().toString("yyyy-MM-dd"),
            "findings": self.scan_results
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4)

    def export_csv(self, file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["target", "vulnerability", "severity", "details"])
            writer.writeheader()
            writer.writerows(self.scan_results)

    def export_pdf(self, file_path):
        template = self.template_combo.currentText()
        pdf = PDFReport(template, self.title_input.text(), self.author_input.text(), QDate.currentDate().toString("yyyy-MM-dd"))

        if template == "Executive":
            pdf.add_executive_summary(self.scan_results)
            pdf.add_recommendations(self.scan_results)
        elif template == "Technical":
            pdf.add_findings(self.scan_results)

        pdf.output(file_path)

    def get_report_metadata(self):
        return {
            "title": self.title_input.text(),
            "author": self.author_input.text(),
            "date": QDate.currentDate().toString("yyyy-MM-dd"),
        }

if __name__ == "__main__":
    logging.info('Generating report')
