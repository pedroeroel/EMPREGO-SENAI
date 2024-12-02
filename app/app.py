from flask import Flask, Blueprint
from app.routes.main.routes import main
from app.routes.auth.routes import auth
from app.routes.company.routes import company
from app.routes.admin.routes import admin
from app.config import SECRET_KEY
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError as e:
        print(f"CRITICAL ERROR creating uploads directory: {e}")
        raise

    # Register blueprints
    app.register_blueprint(main, config={'UPLOAD_FOLDER': app.config['UPLOAD_FOLDER']})
    app.register_blueprint(auth, config={'UPLOAD_FOLDER': app.config['UPLOAD_FOLDER']})
    app.register_blueprint(company, config={'UPLOAD_FOLDER': app.config['UPLOAD_FOLDER']})
    app.register_blueprint(admin, config={'UPLOAD_FOLDER': app.config['UPLOAD_FOLDER']})

    return app
