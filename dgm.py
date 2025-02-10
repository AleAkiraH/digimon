import secure_config
import sys
from PyQt5.QtWidgets import QApplication
from interfaces import MainWindow
from PyQt5.QtCore import Qt

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())