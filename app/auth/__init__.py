from flask import Blueprint
from . import routes

auth = Blueprint('auth', __name__, template_folder='templates')