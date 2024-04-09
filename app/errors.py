from flask import render_template
from app import app, db

"""
- Similar to views, error pages are rendered here
"""

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # database rollback because 500 is a DB error
    return render_template('500.html'), 500