from flask import Blueprint
from . import routes

company = Blueprint('company', __name__, template_folder='templates')