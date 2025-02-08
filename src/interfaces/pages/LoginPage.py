from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QGroupBox, QProgressBar)
from PyQt5.QtCore import Qt
from ..threads.LoginThread import LoginThread

class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._setup_ui()
        
    def _setup_ui(self):
        container = QWidget()
        container.setFixedWidth(400)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(20)
        
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(container)
        
        self._setup_title(container_layout)
        self._setup_login_form(container_layout)
        
    def _setup_title(self, layout):
        title_label = QLabel("Digimon Automation")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #4682B4;
            margin: 20px 0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
    def _setup_login_form(self, container_layout):
        login_form = QGroupBox()
        login_form.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(login_form)
        form_layout.setSpacing(15)
        
        self._setup_input_fields(form_layout)
        self._setup_progress_bar(form_layout)
        self._setup_login_button(form_layout)
        
        container_layout.addWidget(login_form)
        container_layout.addStretch()
        
    def _setup_input_fields(self, layout):
        # Username field
        username_label = QLabel("Username")
        username_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet(self._get_input_style())
        layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self._get_input_style())
        layout.addWidget(self.password_input)
        
    def _setup_progress_bar(self, layout):
        self.login_progress = QProgressBar()
        self.login_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        self.login_progress.hide()
        layout.addWidget(self.login_progress)
        
        self.login_status = QLabel("")
        self.login_status.setStyleSheet("""
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        """)
        self.login_status.setAlignment(Qt.AlignCenter)
        self.login_status.hide()
        layout.addWidget(self.login_status)
        
    def _setup_login_button(self, layout):
        self.login_button = QPushButton("Login")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.login_button.clicked.connect(self.authenticate)
        layout.addWidget(self.login_button)
        
    def _get_input_style(self):
        return """
            QLineEdit {
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4682B4;
            }
        """