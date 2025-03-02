"""Utility functions for the Flask app."""
from flask import request, session, abort

def check_csrf():
    """Check if the CSRF token in the form matches the one in the session."""
    if "csrf_token" not in session or "csrf_token" not in request.form:
        abort(403)

    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
