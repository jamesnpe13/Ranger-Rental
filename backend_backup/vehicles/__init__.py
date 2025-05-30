from flask import Blueprint

bp = Blueprint('vehicles', __name__)

from . import routes
