from .flaskClass import FlaskClass

class AttractionClass(FlaskClass):
    def get_data(self):
        register_info = self.get_register_info()
        return register_info
    
    def get_register_info(self):
        return [
            {"name": "Joe's hello", "category": "food", "distance": 0.5, "liveWaitTime": "5 min"},
            {"name": "Skeeps", "category": "bar", "distance": 1.2, "liveWaitTime": "10 min"},
            {"name": "Panch", "category": "food", "distance": 2.0, "liveWaitTime": "15 min"},
            {"name": "Ricks", "category": "bar", "distance": 0.8, "liveWaitTime": "20 min"}
        ]