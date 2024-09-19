#!/usr/bin/env python3
""" session_auth.py """
from api.v1.views import app_views
from flask import abort, jsonify, request
from models.user import User
from os import getenv


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def login():
    """login function
    """
    user_email = request.form.get('email')

    if not user_email:
        return jsonify({"error": "email missing"}), 400

    user_password = request.form.get('password')

    if not user_password:
        return jsonify({"error": "password missing"}), 400

    try:
        found_users = User.search({'email': user_email})
    except Exception:
        return jsonify({"error": "no user found for this email"}), 404

    if not found_users:
        return jsonify({"error": "no user found for this email"}), 404

    for user in found_users:
        if not user.is_valid_password(user_password):
            return jsonify({"error": "wrong password"}), 401

    from api.v1.app import authentication

    authenticated_user = found_users[0]
    session_id = authentication.create_session(authenticated_user.id)

    session_name = getenv("SESSION_NAME")

    response = jsonify(authenticated_user.to_json())
    response.set_cookie(session_name, session_id)

    return response


@app_views.route('/auth_session/logout', methods=['DELETE'],
                 strict_slashes=False)
def logout():
    """logout function
    """
    from api.v1.app import auth

    if not auth.destroy_session(request):
        abort(404)

    return jsonify({}), 200
