import os
import shutil

from flask import Flask
from flask_session import Session
from . import store

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config["SESSION_TYPE"] = "filesystem"
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SECRET_KEY'] = os.urandom(24).hex()
    app.config['SESSION_FILE_DIR'] = os.path.join(app.instance_path, 'sessions')
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600
    Session(app)

    app.register_blueprint(store.bp)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app