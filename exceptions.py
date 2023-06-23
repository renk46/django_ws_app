class InvalidData(Exception):
    """Exception received invalid data"""
    def __init__(self):
        super().__init__("Invalid Data")

class InvalidCredentials(Exception):
    """Exception invalid data"""
    def __init__(self):
        super().__init__("Invalid Credentials")

class InvalidToken(Exception):
    """Exception invalid token"""
    def __init__(self):
        super().__init__("Invalid Token")
