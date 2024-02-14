from flask import Blueprint

bp = Blueprint("scores", __name__)

from app.scores import routes
