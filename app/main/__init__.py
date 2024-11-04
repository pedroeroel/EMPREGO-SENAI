from flask import Blueprint
from . import routes

main = Blueprint('main', __name__, template_folder='templates')