import sys
import api
import configparser
from typing import Final, Optional, Dict, Any
from threading import Timer
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                             QGroupBox, QSystemTrayIcon, QMenu, QAction, QStyle,
                             QTabWidget, QLineEdit, QSpinBox, QFormLayout,
                             QMessageBox, QFileDialog)
from PyQt5.QtGui import QIcon, QFont


class ActiveWindowMonitor(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        # Load configuration
        self.config_path: Final[Path] = Path("config.ini")
        self.load_config()
        
        self.timer: Optional[Timer] = None
        self.is_monitoring: bool = False
        self.last_upload_status: str = ""
        
        self.init_ui()
        self.init_tray_icon()
        
        # Attempt login
        self.login()
        
    def load_config(self) -> None:
        """Load INI configuration file"""
        self.config: configparser.ConfigParser = configparser.ConfigParser()
        
        try:
            if self.config_path.exists():
                self.config.read(self.config_path, encoding='utf-8')
            else:
                # Create default configuration
                self.create_default_config()
                self.config.read(self.config_path, encoding='utf-8')
                
            # Read configuration values
            self.SERVER_URL: str = self.config.get('Server', 'SERVER_URL', fallback='http://127.0.0.1:5050')
            self.USER_ID: str = self.config.get('Server', 'USER_ID', fallback='YOUR_USER_ID')
            self.USER_NAME: str = self.config.get('Server', 'USER_NAME', fallback='YOUR_USER_NAME')
            self.USER_PASSWORD: str = self.config.get('Server', 'USER_PASSWORD', fallback='YOUR_USER_PASSWORD')
            self.SEND_GAP: int = self.config.getint('Send', 'SEND_GAP', fallback=2000)
                
        except Exception as e:
            QMessageBox.warning(self, "Configuration Loading Error", f"Unable to load configuration file: {e}")
            # Use default values
            self.SERVER_URL = 'http://127.0.0.1:5050'
            self.USER_ID = 'YOUR_USER_ID'
            self.USER_NAME = 'YOUR_USER_NAME'
            self.USER_PASSWORD = 'YOUR_USER_PASSWORD'
            self.SEND_GAP = 2000
        
    def create_default_config(self) -> None:
        """Create default INI configuration file"""
        self.config['Server'] = {
            'SERVER_URL': 'http://127.0.0.1:5050',
            'USER_ID': 'YOUR_USER_ID',
            'USER_NAME': 'YOUR_USER_NAME',
            'USER_PASSWORD': 'YOUR_USER_PASSWORD'
        }
        self.config['Send'] = {
            'SEND_GAP': '2000'
        }
        self.save_config()
        
    def save_config(self) -> bool:
        """Save configuration file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Configuration Saving Error", f"Unable to save configuration file: {e}")
            return False
        
    def init_ui(self) -> None:
        self.setWindowTitle("Active Window Monitor")
        self.setGeometry(300, 300, 700, 600)
        
        # Set application icon
        APP_ICON: Final[QIcon] = QIcon.fromTheme("system-run", 
                                  self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.setWindowIcon(APP_ICON)
        
        # Create tab widget
        self.tab_widget: QTabWidget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Create monitoring page
        self.monitor_tab: QWidget = QWidget()
        self.init_monitor_tab()
        
        # Create configuration page
        self.config_tab: QWidget = QWidget()
        self.init_config_tab()
        
        # Add tabs
        self.tab_widget.addTab(self.monitor_tab, "Monitoring")
        self.tab_widget.addTab(self.config_tab, "Configuration")
        
    def init_monitor_tab(self) -> None:
        """Initialize monitoring tab"""
        MAIN_LAYOUT: Final[QVBoxLayout] = QVBoxLayout(self.monitor_tab)
        
        # Configuration info group
        CONFIG_GROUP: Final[QGroupBox] = QGroupBox("Current Configuration")
        CONFIG_LAYOUT: Final[QVBoxLayout] = QVBoxLayout()
        
        self.user_id_label: QLabel = QLabel(f"User ID: {self.USER_ID}")
        self.user_name_label: QLabel = QLabel(f"Username: {self.USER_NAME}")
        self.server_url_label: QLabel = QLabel(f"Server URL: {self.SERVER_URL}")
        self.send_gap_label: QLabel = QLabel(f"Send Interval: {self.SEND_GAP} ms")
        
        CONFIG_LAYOUT.addWidget(self.user_id_label)
        CONFIG_LAYOUT.addWidget(self.user_name_label)
        CONFIG_LAYOUT.addWidget(self.server_url_label)
        CONFIG_LAYOUT.addWidget(self.send_gap_label)
        CONFIG_GROUP.setLayout(CONFIG_LAYOUT)
        
        # Status info group
        STATUS_GROUP: Final[QGroupBox] = QGroupBox("Status Information")
        STATUS_LAYOUT: Final[QVBoxLayout] = QVBoxLayout()
        
        self.login_status_label: QLabel = QLabel("Login Status: Not Logged In")
        self.monitor_status_label: QLabel = QLabel("Monitoring Status: Stopped")
        self.last_upload_label: QLabel = QLabel("Last Upload: None")
        
        STATUS_LAYOUT.addWidget(self.login_status_label)
        STATUS_LAYOUT.addWidget(self.monitor_status_label)
        STATUS_LAYOUT.addWidget(self.last_upload_label)
        STATUS_GROUP.setLayout(STATUS_LAYOUT)
        
        # Control buttons group
        BUTTON_LAYOUT: Final[QHBoxLayout] = QHBoxLayout()
        
        self.start_button: QPushButton = QPushButton("Start Monitoring")
        self.stop_button: QPushButton = QPushButton("Stop Monitoring")
        self.refresh_config_button: QPushButton = QPushButton("Refresh Config")
        self.exit_button: QPushButton = QPushButton("Exit")
        
        self.stop_button.setEnabled(False)
        
        BUTTON_LAYOUT.addWidget(self.start_button)
        BUTTON_LAYOUT.addWidget(self.stop_button)
        BUTTON_LAYOUT.addWidget(self.refresh_config_button)
        BUTTON_LAYOUT.addWidget(self.exit_button)
        
        # Log display
        LOG_GROUP: Final[QGroupBox] = QGroupBox("Log")
        LOG_LAYOUT: Final[QVBoxLayout] = QVBoxLayout()
        
        self.log_text: QTextEdit = QTextEdit()
        self.log_text.setReadOnly(True)
        FONT: Final[QFont] = QFont("Microsoft YaHei", 10)
        self.log_text.setFont(FONT)
        
        LOG_LAYOUT.addWidget(self.log_text)
        LOG_GROUP.setLayout(LOG_LAYOUT)
        
        # Add to main layout
        MAIN_LAYOUT.addWidget(CONFIG_GROUP)
        MAIN_LAYOUT.addWidget(STATUS_GROUP)
        MAIN_LAYOUT.addWidget(LOG_GROUP)
        MAIN_LAYOUT.addLayout(BUTTON_LAYOUT)
        
        # Connect signals and slots
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.refresh_config_button.clicked.connect(self.refresh_config)
        self.exit_button.clicked.connect(self.close_application)
        
        # Add log entries
        self.add_log("Application initialized")
        self.add_log(f"User: {self.USER_NAME} ({self.USER_ID})")
        self.add_log(f"Server: {self.SERVER_URL}")
        self.add_log(f"Send Interval: {self.SEND_GAP} ms")
        
    def init_config_tab(self) -> None:
        """Initialize configuration editing tab"""
        MAIN_LAYOUT: Final[QVBoxLayout] = QVBoxLayout(self.config_tab)
        
        # Server configuration group
        SERVER_GROUP: Final[QGroupBox] = QGroupBox("Server Configuration")
        SERVER_LAYOUT: Final[QFormLayout] = QFormLayout()
        
        self.server_url_edit: QLineEdit = QLineEdit(self.SERVER_URL)
        self.user_id_edit: QLineEdit = QLineEdit(self.USER_ID)
        self.user_name_edit: QLineEdit = QLineEdit(self.USER_NAME)
        self.user_password_edit: QLineEdit = QLineEdit(self.USER_PASSWORD)
        self.user_password_edit.setEchoMode(QLineEdit.Password)
        
        SERVER_LAYOUT.addRow("Server URL:", self.server_url_edit)
        SERVER_LAYOUT.addRow("User ID:", self.user_id_edit)
        SERVER_LAYOUT.addRow("Username:", self.user_name_edit)
        SERVER_LAYOUT.addRow("Password:", self.user_password_edit)
        SERVER_GROUP.setLayout(SERVER_LAYOUT)
        
        # Send configuration group
        SEND_GROUP: Final[QGroupBox] = QGroupBox("Send Configuration")
        SEND_LAYOUT: Final[QFormLayout] = QFormLayout()
        
        self.send_gap_spin: QSpinBox = QSpinBox()
        self.send_gap_spin.setRange(100, 60000)  # 100ms to 60s
        self.send_gap_spin.setValue(self.SEND_GAP)
        self.send_gap_spin.setSuffix(" ms")
        
        SEND_LAYOUT.addRow("Send Interval:", self.send_gap_spin)
        SEND_GROUP.setLayout(SEND_LAYOUT)
        
        # Configuration action buttons
        BUTTON_LAYOUT: Final[QHBoxLayout] = QHBoxLayout()
        
        self.save_button: QPushButton = QPushButton("Save Configuration")
        self.reset_button: QPushButton = QPushButton("Reset")
        self.load_button: QPushButton = QPushButton("Load from File")
        self.export_button: QPushButton = QPushButton("Export Configuration")
        
        BUTTON_LAYOUT.addWidget(self.save_button)
        BUTTON_LAYOUT.addWidget(self.reset_button)
        BUTTON_LAYOUT.addWidget(self.load_button)
        BUTTON_LAYOUT.addWidget(self.export_button)
        
        # Add to main layout
        MAIN_LAYOUT.addWidget(SERVER_GROUP)
        MAIN_LAYOUT.addWidget(SEND_GROUP)
        MAIN_LAYOUT.addLayout(BUTTON_LAYOUT)
        MAIN_LAYOUT.addStretch()
        
        # Connect signals and slots
        self.save_button.clicked.connect(self.save_config_changes)
        self.reset_button.clicked.connect(self.reset_config_form)
        self.load_button.clicked.connect(self.load_config_from_file)
        self.export_button.clicked.connect(self.export_config)
        
    def init_tray_icon(self) -> None:
        self.tray_icon: QSystemTrayIcon = QSystemTrayIcon(self)
        TRAY_ICON: Final[QIcon] = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(TRAY_ICON)
        
        # Create tray menu
        tray_menu: Final[QMenu] = QMenu()
        
        show_action: Final[QAction] = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        
        hide_action: Final[QAction] = QAction("Hide Window", self)
        hide_action.triggered.connect(self.hide)
        
        exit_action: Final[QAction] = QAction("Exit", self)
        exit_action.triggered.connect(self.close_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Tray icon click event
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
    def on_tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
                
    def login(self) -> None:
        self.add_log("Logging in...")
        login_results: Final[Dict[str, Any]] = api.login_web(
            self.USER_ID, self.USER_NAME, self.USER_PASSWORD, self.SERVER_URL
        )
        
        if login_results["status"] == "success":
            self.login_status_label.setText("Login Status: Logged In")
            self.add_log("Login successful")
            self.start_button.setEnabled(True)
        else:
            self.login_status_label.setText("Login Status: Failed")
            self.add_log(f"Login failed: {login_results['message']}")
            self.start_button.setEnabled(False)
            
    def get_active_window_title(self) -> None:
        active_window: Final[Optional[str]] = api.get_active_window_title()

        if not active_window:
            self.add_log(f"[Active window] No active window found.")
            self.timer = Timer(self.SEND_GAP / 1000, self.get_active_window_title)
            self.timer.start()
            return
        
        self.add_log(f"[Active window] {active_window}")
        
        upload_results: Final[Dict[str, Any]] = api.upload_info(
            self.USER_ID, self.USER_NAME, self.USER_PASSWORD, 
            active_window, self.SERVER_URL
        )
        
        current_time: Final[str] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if upload_results["status"] == "success":
            self.last_upload_status = "Success"
            self.add_log(f"[Upload] Upload successful at {current_time}")
        else:
            self.last_upload_status = f"Failed: {upload_results['message']}"
            self.add_log(f"[Upload] Upload failed at {current_time}: {upload_results['message']}")
            
        self.last_upload_label.setText(f"Last Upload: {current_time} ({self.last_upload_status})")
            
        if self.is_monitoring:
            self.timer = Timer(self.SEND_GAP / 1000, self.get_active_window_title)
            self.timer.start()
            
    def start_monitoring(self) -> None:
        self.is_monitoring = True
        self.monitor_status_label.setText("Monitoring Status: Running")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.add_log("Started monitoring active window")
        
        self.get_active_window_title()
        
    def stop_monitoring(self) -> None:
        self.is_monitoring = False
        self.monitor_status_label.setText("Monitoring Status: Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.add_log("Stopped monitoring active window")
        
        if self.timer:
            self.timer.cancel()
            
    def refresh_config(self) -> None:
        """Refresh configuration display"""
        self.load_config()
        self.update_config_display()
        self.add_log("Configuration refreshed")
        
    def update_config_display(self) -> None:
        """Update configuration display on monitoring page"""
        self.user_id_label.setText(f"User ID: {self.USER_ID}")
        self.user_name_label.setText(f"Username: {self.USER_NAME}")
        self.server_url_label.setText(f"Server URL: {self.SERVER_URL}")
        self.send_gap_label.setText(f"Send Interval: {self.SEND_GAP} ms")
        
    def save_config_changes(self) -> None:
        """Save configuration changes"""
        # Update configuration
        self.config['Server']['SERVER_URL'] = self.server_url_edit.text()
        self.config['Server']['USER_ID'] = self.user_id_edit.text()
        self.config['Server']['USER_NAME'] = self.user_name_edit.text()
        self.config['Server']['USER_PASSWORD'] = self.user_password_edit.text()
        self.config['Send']['SEND_GAP'] = str(self.send_gap_spin.value())
        
        # Save to file
        if self.save_config():
            # Reload configuration
            self.load_config()
            self.update_config_display()
            self.add_log("Configuration saved and applied")
            QMessageBox.information(self, "Success", "Configuration saved and applied")
            
    def reset_config_form(self) -> None:
        """Reset configuration form to current values"""
        self.server_url_edit.setText(self.SERVER_URL)
        self.user_id_edit.setText(self.USER_ID)
        self.user_name_edit.setText(self.USER_NAME)
        self.user_password_edit.setText(self.USER_PASSWORD)
        self.send_gap_spin.setValue(self.SEND_GAP)
        self.add_log("Configuration form reset")
        
    def load_config_from_file(self) -> None:
        """Load configuration from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Configuration File", "", "INI Files (*.ini);;All Files (*)"
        )
        
        if file_path:
            try:
                new_config = configparser.ConfigParser()
                new_config.read(file_path, encoding='utf-8')
                
                # Update current configuration
                for section in new_config.sections():
                    if section not in self.config:
                        self.config.add_section(section)
                    for key, value in new_config.items(section):
                        self.config[section][key] = value
                
                if self.save_config():
                    self.load_config()
                    self.reset_config_form()
                    self.update_config_display()
                    self.add_log(f"Configuration loaded from file: {file_path}")
                    QMessageBox.information(self, "Success", "Configuration loaded and applied from file")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load configuration file: {e}")
                
    def export_config(self) -> None:
        """Export configuration to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration File", "config.ini", "INI Files (*.ini);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as configfile:
                    self.config.write(configfile)
                self.add_log(f"Configuration exported to: {file_path}")
                QMessageBox.information(self, "Success", "Configuration exported")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export configuration: {e}")
        
    def add_log(self, message: str) -> None:
        timestamp: Final[str] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def close_application(self) -> None:
        self.stop_monitoring()
        self.tray_icon.hide()
        QApplication.quit()
        
    def closeEvent(self, a0: Any) -> None:
        a0.ignore()
        self.hide()
        self.add_log("Window hidden to system tray, double-click tray icon to show again")


def main() -> None:
    APP: Final[QApplication] = QApplication(sys.argv)
    APP.setQuitOnLastWindowClosed(False)
    
    font = QFont("Microsoft YaHei", 10)
    
    APP.setFont(font)
    
    MONITOR: Final[ActiveWindowMonitor] = ActiveWindowMonitor()
    MONITOR.show()
    
    sys.exit(APP.exec_())


if __name__ == "__main__":
    main()