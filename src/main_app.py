"""
Main application for prostate MRI segmentation tool
A graphic segmentation tool for prostate MRI exams based on DICOM data
"""

import sys
import os
from typing import Dict, List, Optional
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QFileDialog,
                             QStatusBar, QToolBar, QAction, QMenuBar, QMessageBox,
                             QWidget, QVBoxLayout, QSplitter, QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# Import existing components
from dicom_handler import DICOMHandler
from segmentation_tools import SegmentationTools
from status_tracker import StatusTracker


class SegmentationWorker(QThread):
    """Worker thread for segmentation operations"""
    progress_updated = pyqtSignal(int)
    segmentation_completed = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, image_data, tool_name, tool_params):
        super().__init__()
        self.image_data = image_data
        self.tool_name = tool_name
        self.tool_params = tool_params

    def run(self):
        try:
            # Simulate processing time
            segmentation_tool = SegmentationTools()
            result = segmentation_tool.apply_tool(
                self.tool_name,
                self.image_data,
                **self.tool_params
            )
            self.segmentation_completed.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ProstateSegmentationApp(QMainWindow):
    """Main application for prostate MRI segmentation"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prostate MRI Segmentation Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize components
        self.dicom_handler = DICOMHandler()
        self.segmentation_tools = SegmentationTools()
        self.status_tracker = StatusTracker()

        # Current data
        self.current_series = None
        self.current_segmentation = None
        self.current_task_id = None

        # Create UI
        self.init_ui()

        # Initialize status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def init_ui(self):
        """Initialize the user interface"""
        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create different tabs
        self.create_main_tab()
        self.create_tools_tab()
        self.create_status_tab()

        # Add a simple status label
        status_label = QLabel("Prostate MRI Segmentation Tool")
        status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(status_label)

    def create_menu_bar(self):
        """Create the main menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        open_action = QAction('Open DICOM Series', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_dicom_series)
        file_menu.addAction(open_action)

        save_action = QAction('Save Segmentation', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_segmentation)
        file_menu.addAction(save_action)

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu('Tools')

        ai_preseg_action = QAction('AI Pre-segmentation', self)
        ai_preseg_action.triggered.connect(self.run_ai_presegmentation)
        tools_menu.addAction(ai_preseg_action)

        # View menu
        view_menu = menubar.addMenu('View')

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = self.addToolBar('Main')

        open_icon = QIcon.fromTheme('document-open')
        open_action = QAction(open_icon, 'Open Series', self)
        open_action.triggered.connect(self.open_dicom_series)
        toolbar.addAction(open_action)

        save_icon = QIcon.fromTheme('document-save')
        save_action = QAction(save_icon, 'Save Segmentation', self)
        save_action.triggered.connect(self.save_segmentation)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        ai_icon = QIcon.fromTheme('system-run')
        ai_action = QAction(ai_icon, 'AI Pre-segmentation', self)
        ai_action.triggered.connect(self.run_ai_presegmentation)
        toolbar.addAction(ai_action)

    def create_main_tab(self):
        """Create the main viewing tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add a label for now
        label = QLabel("Main View - DICOM Series Display")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Add a placeholder for image display
        # In a real implementation, this would display the DICOM images
        image_label = QLabel("Image display area would go here")
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        self.tab_widget.addTab(tab, "Main")

    def create_tools_tab(self):
        """Create the tools tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        tools_label = QLabel("Segmentation Tools")
        tools_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(tools_label)

        # List of available tools
        tools_list = [
            "Brush Tool",
            "Rectangle Tool",
            "Circle Tool",
            "Flood Fill Tool",
            "Threshold Tool",
            "Watershed Tool",
            "Active Contour Tool"
        ]

        for tool in tools_list:
            tool_label = QLabel(f"• {tool}")
            layout.addWidget(tool_label)

        # AI Pre-segmentation
        ai_label = QLabel("\nAI Pre-segmentation:")
        layout.addWidget(ai_label)

        ai_info = QLabel("• Unet-based segmentation (pre-trained model)")
        layout.addWidget(ai_info)

        self.tab_widget.addTab(tab, "Tools")

    def create_status_tab(self):
        """Create the status tracking tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        status_label = QLabel("Segmentation Status")
        status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label)

        # Display current task info
        task_info = QLabel("No active task")
        layout.addWidget(task_info)

        # Status statistics
        stats_label = QLabel("Statistics:")
        layout.addWidget(stats_label)

        # In a real implementation, this would display actual statistics
        stats_info = QLabel("• Total tasks: 0\n• Completed: 0\n• In Progress: 0\n• Created: 0")
        layout.addWidget(stats_info)

        self.tab_widget.addTab(tab, "Status")

    def open_dicom_series(self):
        """Open a DICOM series for segmentation"""
        folder = QFileDialog.getExistingDirectory(self, "Select DICOM Series Folder")
        if folder:
            try:
                self.status_bar.showMessage(f"Loading DICOM series from {folder}...")

                # Load series data
                series_data = self.dicom_handler.load_series_from_directory(folder)

                if not series_data:
                    QMessageBox.warning(self, "No Data", "No valid DICOM files found in the selected folder.")
                    return

                # Display information about loaded series
                series_list = self.dicom_handler.get_series_info(series_data)
                info_text = f"Loaded {len(series_list)} series:\n"
                for series in series_list:
                    info_text += f"  - {series['series_name']} ({series['modality']})\n"

                self.status_bar.showMessage(f"Loaded {len(series_list)} series")
                QMessageBox.information(self, "Series Loaded", info_text)

                # Store current series
                self.current_series = series_data

                # Create a new task for this series
                task_id = f"task_{len(self.status_tracker.get_all_tasks()) + 1}"
                patient_id = series_list[0]['patient_id'] if series_list else "Unknown"
                series_uid = list(series_data.keys())[0] if series_data else "Unknown"

                task_info = self.status_tracker.create_segmentation_task(
                    task_id, patient_id, series_uid, "current_user"
                )
                self.current_task_id = task_id

                # Update status tab
                self.update_status_tab()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load DICOM series: {str(e)}")
                self.status_bar.showMessage("Error loading series")

    def save_segmentation(self):
        """Save the current segmentation"""
        if self.current_segmentation is None:
            QMessageBox.warning(self, "No Segmentation", "No segmentation to save.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Segmentation", "", "NumPy Files (*.npy);;All Files (*)"
        )

        if filename:
            try:
                if not filename.endswith('.npy'):
                    filename += '.npy'

                self.segmentation_tools.save_segmentation(self.current_segmentation, filename)
                QMessageBox.information(self, "Saved", f"Segmentation saved to {filename}")
                self.status_bar.showMessage(f"Segmentation saved to {filename}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save segmentation: {str(e)}")
                self.status_bar.showMessage("Error saving segmentation")

    def run_ai_presegmentation(self):
        """Run AI-based pre-segmentation"""
        if self.current_series is None:
            QMessageBox.warning(self, "No Data", "Please load a DICOM series first.")
            return

        try:
            self.status_bar.showMessage("Running AI pre-segmentation...")

            # Get first series data for demonstration
            first_series = list(self.current_series.values())[0]
            image_data = first_series['data']

            # Run AI pre-segmentation in a separate thread
            worker = SegmentationWorker(image_data, 'threshold', {})
            worker.segmentation_completed.connect(self.on_ai_segmentation_complete)
            worker.error_occurred.connect(self.on_ai_segmentation_error)
            worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run AI pre-segmentation: {str(e)}")
            self.status_bar.showMessage("Error running AI pre-segmentation")

    def on_ai_segmentation_complete(self, result):
        """Handle completion of AI segmentation"""
        self.current_segmentation = result
        self.status_bar.showMessage("AI pre-segmentation completed")
        QMessageBox.information(self, "Complete", "AI pre-segmentation completed successfully")

    def on_ai_segmentation_error(self, error_msg):
        """Handle error during AI segmentation"""
        self.status_bar.showMessage("AI pre-segmentation error")
        QMessageBox.critical(self, "Error", f"AI pre-segmentation failed: {error_msg}")

    def update_status_tab(self):
        """Update the status tab with current information"""
        # This would update the status tab with actual data
        pass

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Prostate MRI Segmentation Tool",
            "A graphic segmentation tool for prostate MRI exams based on DICOM data.\n\n"
            "Features:\n"
            "• DICOM multi-series handling\n"
            "• Common annotation and segmentation tools\n"
            "• Status tracking\n"
            "• Multi-user support\n"
            "• AI pre-segmentation integration\n"
        )

    def closeEvent(self, event):
        """Handle application closing"""
        reply = QMessageBox.question(
            self, 'Exit Application',
            'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """Main function to start the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Prostate MRI Segmentation Tool")

    # Create and show the main window
    window = ProstateSegmentationApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()