from flaskClass import FlaskClass

class NearbyRestaurantsClass(FlaskClass):
    def __init__(self, regInfo):
        self.regInfo = regInfo

    def get_data(self):
        return "hello"
    
     