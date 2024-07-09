import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User, Post

#shell_context_processor run when we start flask shell, it returns flask app instance, db instance and some more things that require 
#import at a lot of places
@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}