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
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads/')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(company)
    app.register_blueprint(admin)

    return app
