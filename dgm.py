import secure_config
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from interfaces import MainWindow

if __name__ == "__main__":
    # Enable High DPI support before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())