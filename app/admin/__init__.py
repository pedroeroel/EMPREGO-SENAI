from flask import Blueprint
from . import routes

admin = Blueprint('admin', __name__, template_folder='templates')