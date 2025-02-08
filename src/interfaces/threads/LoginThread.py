from PyQt5.QtCore import QThread, pyqtSignal

class LoginThread(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)

    def __init__(self, db, username, password):
        super().__init__()
        self.db = db
        self.username = username
        self.password = password

    def run(self):
        try:
            self.progress.emit(10)

            version_valid, version_error = self.db.validate_version()
            if not version_valid:
                self.finished.emit(False, version_error)
                return
            self.progress.emit(30)

            is_valid, error_message = self.db.validate_user(self.username, self.password)
            if not is_valid:
                self.finished.emit(False, error_message if error_message else "Credenciais inválidas!")
                return
            self.progress.emit(60)

            self.progress.emit(90)
            self.finished.emit(True, None)
            self.progress.emit(99)

        except Exception as e:
            self.finished.emit(False, f"Erro ao conectar ao banco de dados: {str(e)}")