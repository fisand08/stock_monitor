from app import app
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User, Portfolio

"""
helps running the app
"""

"""
Shell context that allows to run "flask shell" in command line
launching flask-aware python interpreter
"""
@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Portfolio': Portfolio}