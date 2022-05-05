import os

from flask import Flask
from . import store

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = "6c561d02ec26c8059649faaaf994a68b53c3b1a4f001df9c"

    app.register_blueprint(store.bp)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app