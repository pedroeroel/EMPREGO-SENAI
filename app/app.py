from flask import Flask, Blueprint
from app.main.routes import main
from app.auth.routes import auth
from app.company.routes import company
from app.admin.routes import admin
from app.config import SECRET_KEY

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(company)
    app.register_blueprint(admin)

    return app
