#!/usr/bin/env python3
""" app.py """
from auth import Authentication
from flask import Flask, jsonify, request, abort, redirect


auth_service = Authentication()
web_app = Flask(__name__)


@web_app.route('/', methods=['GET'], strict_slashes=False)
def welcome() -> str:
    """welcome function
    """
    return jsonify({"message": "Bienvenue"}), 200


@web_app.route('/users', methods=['POST'], strict_slashes=False)
def create_user() -> str:
    """create_user function
    """
    user_email = request.form.get('email')
    user_password = request.form.get('password')
    try:
        auth_service.register_user(user_email, user_password)
        return jsonify(
            {"email": f"{user_email}", "message": "user created"}), 200
    except Exception:
        return jsonify({"message": "email already registered"}), 400


@web_app.route('/sessions', methods=['POST'], strict_slashes=False)
def login() -> str:
    """login function
    """
    user_email = request.form.get('email')
    user_password = request.form.get('password')
    is_valid_login = auth_service.valid_login(user_email, user_password)
    if is_valid_login:
        session_token = auth_service.create_session(user_email)
        response = jsonify({"email": f"{user_email}", "message": "logged in"})
        response.set_cookie('session_id', session_token)
        return response
    else:
        abort(401)


@web_app.route('/sessions', methods=['DELETE'], strict_slashes=False)
def logout() -> str:
    """logout function
    """
    session_token = request.cookies.get('session_id')
    user = auth_service.get_user_from_session_id(session_token)
    if user:
        auth_service.destroy_session(user.id)
        return redirect('/')
    else:
        abort(403)


@web_app.route('/profile', methods=['GET'], strict_slashes=False)
def profile() -> str:
    """profile function
    """
    session_token = request.cookies.get('session_id')
    user = auth_service.get_user_from_session_id(session_token)
    if user:
        return jsonify({"email": user.email}), 200
    else:
        abort(403)


@web_app.route('/reset_password', methods=['POST'], strict_slashes=False)
def get_reset_password_token() -> str:
    """get_reset_password_token function
    """
    user_email = request.form.get('email')
    user = auth_service.create_session(user_email)
    if not user:
        abort(403)
    else:
        reset_token = auth_service.get_reset_password_token(user_email)
        return jsonify(
            {"email": f"{user_email}", "reset_token": f"{reset_token}"})


@web_app.route('/reset_password', methods=['PUT'], strict_slashes=False)
def update_password() -> str:
    """update_password function
    """
    user_email = request.form.get('email')
    reset_token = request.form.get('reset_token')
    new_password = request.form.get('new_password')
    try:
        auth_service.update_password(reset_token, new_password)
        return jsonify({"email": f"{user_email}",
                        "message": "Password updated"}), 200
    except Exception:
        abort(403)


if __name__ == "__main__":
    """__main__
    """
    web_app.run(host="0.0.0.0", port="5000")
