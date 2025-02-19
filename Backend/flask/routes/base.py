from flask import Flask
from attractions import bp as attraction_bp
# from search import bp as search_bp
# from company import bp as company_bp
# from flashcard import bp as flashcard_bp
app = Flask(__name__)

app.register_blueprint(attraction_bp)
# app.register_blueprint(search_bp)
# app.register_blueprint(company_bp)
# app.register_blueprint(flashcard_bp)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)