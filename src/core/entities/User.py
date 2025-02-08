class User:
    def __init__(self, username: str, password: str):
        self.username = username.lower()
        self.password = password
        self.is_authenticated = False
        self.license_expiration = None