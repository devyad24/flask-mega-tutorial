from flask import Blueprint

bp = Blueprint('errors', __name__)

#Importing in last to avoid circular dependency
from app.errors import handlers