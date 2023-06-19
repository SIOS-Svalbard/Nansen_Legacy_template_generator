from flask import Flask
import uuid
import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_PATH, 'website', 'config', 'template_configurations.yaml')
DROPDOWNS_PATH = os.path.join(BASE_PATH, 'website', 'config', 'dropdown_lists')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(uuid.uuid4())

    return app
