from flaskClass import FlaskClass

class RegisterClass(FlaskClass):
    def __init__(self, regInfo):
        self.regInfo = regInfo

    def get_data(self):
        register_info = 1
        return register_info
    
    def get_register_info(self):
        return {
            "message": "User registered successfully.",
            "user_id": "UUID"
        }       