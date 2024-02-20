from flask import Blueprint

bp = Blueprint("subjects", __name__)

from app.subjects import routes
