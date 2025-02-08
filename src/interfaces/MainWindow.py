from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from .pages.LoginPage import LoginPage
from .pages.PlayPage import PlayPage
from .pages.ConfigPage import ConfigPage
from variables import APP_STATES

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digimon Automation")
        self.setGeometry(100, 100, 800, 600)
        self._setup_ui()
        self._setup_state()
        
    def _setup_ui(self):
        self.setStyleSheet(self._get_main_style())
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Initialize pages
        self.login_page = LoginPage(self)
        self.play_page = PlayPage(self)
        self.config_page = ConfigPage(self)

        # Add pages to tabs
        self.tabs.addTab(self.login_page, "Login")
        self.tabs.addTab(self.play_page, "Jogar")
        self.tabs.addTab(self.config_page, "Configurar")

        # Disable tabs until login
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        
    def _setup_state(self):
        self.is_authenticated = False
        self.current_user = None
        self.app_state = APP_STATES['STOPPED']
        self.license_expiration = None
        
    def _get_main_style(self):
        return """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #4682B4;
                color: white;
                padding: 10px 20px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 14px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #1E90FF;
            }
        """