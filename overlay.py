from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QSystemTrayIcon, QMenu
from PyQt5.QtCore import Qt, QPoint, QSize, QTimer, QFileSystemWatcher
from PyQt5.QtGui import QFont, QPainter, QColor, QIcon
import sys
import xml.etree.ElementTree as ET
import os
import json
from datetime import datetime

class OverlayApp(QLabel):
    def __init__(self):
        super().__init__()
        # Set minimum size
        # Close button
        self.font_size = 20  # Track current font size
        self.close_button = QPushButton("X", self)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: red; 
                color: white; 
                border: none; 
                font-size: 16px; 
                font-weight: bold;
                width: 20px;
                height: 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        self.close_button.setFixedSize(20, 20)
        # Position close button at top-right with 5px margin
        self.close_button.move(self.width() - 25, 5)
        self.close_button.raise_()  # Ensure button stays on top
        self.close_button.hide()  # Initially hide the close button
        self.close_button.clicked.connect(self.hide)
        
        # Timer for delayed close button hiding
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self.close_button.hide)
        
        # Enable dragging
        self._drag_active = False
        self._drag_position = QPoint()
        
        # Setup XML file monitoring
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.xml_path = config['xml_path']
                self.xml_config = config.get('xml_config', {
                    'root_node': 'root',
                    'target_node': 'DatabaseName',
                    'xpath': './/DatabaseName'
                })
        except Exception as e:
            self.xml_path = ""
            self.xml_config = {
                'root_node': 'root',
                'target_node': 'DatabaseName',
                'xpath': './/DatabaseName'
            }
            print(f"Error loading config.json: {str(e)}")
        self.last_modified = None
        
        self.setMinimumSize(300, 40)
        self.setText("My Text")
        self.setFont(QFont("Arial", self.font_size, QFont.Bold))
        self.setStyleSheet("color: white; background: transparent; padding: 25px 10px 10px 10px;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.move(300, 200)  # Initial position
        
        # Configure window properties and show
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.CustomizeWindowHint |
            Qt.MSWindowsFixedSizeDialogHint |
            Qt.NoDropShadowWindowHint |
            Qt.Tool
        )
        self.setProperty("_q_windowsDropShadow", False)  # Disable drop shadow which can affect stacking
        self.show()
        
        # Setup system tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(self.style().standardIcon(self.style().SP_ComputerIcon)))
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show Overlay")
        show_action.triggered.connect(self.show_overlay)
        hide_action = tray_menu.addAction("Hide Overlay")
        hide_action.triggered.connect(self.hide)
        
        # Add text size controls
        tray_menu.addSeparator()
        increase_size = tray_menu.addAction("Increase Text Size")
        increase_size.triggered.connect(self.increase_text_size)
        decrease_size = tray_menu.addAction("Decrease Text Size")
        decrease_size.triggered.connect(self.decrease_text_size)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Setup timer to ensure window stays on top
        self.stay_on_top_timer = QTimer(self)
        self.stay_on_top_timer.timeout.connect(self.ensure_on_top)
        self.stay_on_top_timer.start(100)  # Check every 100ms
        
        # Setup file system watcher for XML file monitoring
        self.file_watcher = QFileSystemWatcher(self)
        if os.path.exists(self.xml_path):
            self.add_file_to_watcher()
        self.file_watcher.fileChanged.connect(self.check_xml_file)
        
        # Initial XML read
        self.check_xml_file()
    
    def show_overlay(self):
        self.show()
        self.raise_()
        self.activateWindow()
        
    def increase_text_size(self):
        self.font_size = min(72, self.font_size + 2)  # Maximum size of 72
        self.update_font()
        
    def decrease_text_size(self):
        self.font_size = max(8, self.font_size - 2)  # Minimum size of 8
        self.update_font()
        
    def update_font(self):
        font = self.font()
        font.setPointSize(self.font_size)
        self.setFont(font)
        self.adjustSize()  # Adjust window size to fit new text size
    
    def quit_application(self):
        self.tray_icon.hide()
        QApplication.quit()
        
    def closeEvent(self, event):
        event.ignore()
        self.hide()
    
    def ensure_on_top(self):
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        
    def add_file_to_watcher(self):
        # Remove path if it's already being watched
        if self.xml_path in self.file_watcher.files():
            self.file_watcher.removePath(self.xml_path)
        self.file_watcher.addPath(self.xml_path)
        
    def check_xml_file(self):
        try:
            if os.path.exists(self.xml_path):
                modified_time = os.path.getmtime(self.xml_path)
                if self.last_modified != modified_time:
                    self.last_modified = modified_time
                    tree = ET.parse(self.xml_path)
                    root = tree.getroot()
                    db_name = root.find(self.xml_config['xpath'])
                    if db_name is not None:
                        self.setText(db_name.text)
                        # Force an update of the window
                        self.update()
                    else:
                        self.setText(f"Error: {self.xml_config['target_node']} not found in XML")
                # Re-add the file to the watcher
                QTimer.singleShot(100, self.add_file_to_watcher)
        except Exception as e:
            self.setText(f"Error reading XML: {str(e)}")
        
    def sizeHint(self):
        # Provide a reasonable default size
        return QSize(400, 60)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False

    def resizeEvent(self, event):
        # Update close button position when window resizes
        self.close_button.move(self.width() - 25, 5)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw shadow first
        painter.setPen(QColor(0, 0, 0, 127))
        painter.drawText(self.rect().adjusted(2, 2, 2, 2), Qt.AlignCenter, self.text())
        
        # Draw main text
        painter.setPen(Qt.white)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
        
    def enterEvent(self, event):
        self.hide_timer.stop()  # Cancel any pending hide
        self.close_button.show()
        
    def leaveEvent(self, event):
        self.hide_timer.stop()  # Reset timer if already running
        self.hide_timer.start(1500)  # 1.5 seconds

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = OverlayApp()
    sys.exit(app.exec_())