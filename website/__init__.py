from flask import Flask
import uuid

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(uuid.uuid1())

    return app
