#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from api.v1.views import app_views
from api.v1.auth.auth import Auth
from api.v1.auth.basic_auth import BasicAuth
from api.v1.auth.session_auth import SessionAuth
from api.v1.auth.session_exp_auth import SessionExpAuth
from api.v1.auth.session_db_auth import SessionDBAuth
from flask import Flask, jsonify, abort, request
from flask_cors import CORS
import os


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})


authentication = None


if getenv("AUTH_TYPE") == "basic_auth":
    authentication = BasicAuth()
elif getenv("AUTH_TYPE") == "session_auth":
    authentication = SessionAuth()
elif getenv("AUTH_TYPE") == "session_exp_auth":
    authentication = SessionExpAuth()
elif getenv("AUTH_TYPE") == "session_db_auth":
    authentication = SessionDBAuth()
else:
    authentication = Auth()


@app.errorhandler(404)
def not_found(error) -> str:
    """ Not found handler
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> str:
    """Handler for 401 errors
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """Handler for 403 errors
    """
    return jsonify({"error": "Forbidden"}), 403


@app.before_request
def before_request():
    """Handler before request
    """
    excluded_paths = [
        '/api/v1/status/',
        '/api/v1/unauthorized/',
        '/api/v1/forbidden/',
        '/api/v1/auth_session/login/'
    ]

    if authentication and authentication.require_auth(
            request.path, excluded_paths):
        if (not authentication.authorization_header(request) and not
                authentication.session_cookie(request)):
            abort(401)
        if not authentication.current_user(request):
            abort(403)
        request.current_user = authentication.current_user(request)


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
