from .flaskClass import FlaskClass
from ....database import view_locations

class AttractionClass(FlaskClass):
    def get_data(self):
        register_info = self.get_register_info()
        return register_info
    
    def get_register_info(self):
        rows = view_locations()
        reg_info = []
        for row in rows:
            t = "food"
            for types in row[6]:
                if types == "bar":
                    t = "bar"
            reg_info.append({"id": row[0], "name": row[2], "category": t, "distance": 0.1, "liveWaitTime": "5 min"})

        return reg_info
    

def main():
    inst = AttractionClass(1)
    print(inst.get_data())

if __name__ == "__main__":
    main()