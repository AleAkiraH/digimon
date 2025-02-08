from typing import Tuple
from ..entities.User import User
from ...infrastructure.database.Database import Database

class AuthenticationUseCase:
    def __init__(self, database: Database):
        self.database = database
    
    def authenticate(self, user: User) -> Tuple[bool, str]:
        try:
            version_valid, version_error = self.database.validate_version()
            if not version_valid:
                return False, version_error
            
            is_valid, error_message = self.database.validate_user(user.username, user.password)
            if not is_valid:
                return False, error_message if error_message else "Credenciais inválidas!"
            
            user.is_authenticated = True
            user.license_expiration = self.database.get_license_expiration(user.username)
            self.database.record_action(user.username, "login")
            
            return True, None
            
        except Exception as e:
            return False, f"Erro ao conectar ao banco de dados: {str(e)}"