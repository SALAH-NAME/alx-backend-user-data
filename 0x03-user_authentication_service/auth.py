#!/usr/bin/env python3
""" auth.py """
from db import Database
from typing import TypeVar
from user import User
import bcrypt
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound


def hash_password(password: str) -> str:
    """hash_password function
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def generate_uuid() -> str:
    """generate_uuid function
    """
    return str(uuid4())


class Auth:
    """
    Authentication class to interact with the authentication database.
    """

    def __init__(self):
        """__init__
        """
        self._database = Database()

    def register_user(self, email: str, password: str) -> User:
        """register_user function
        """
        try:
            self._database.find_user_by(email=email)
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            return self._database.add_user(email, hash_password(password))

    def valid_login(self, email: str, password: str) -> bool:
        """valid_login function
        """
        try:
            user = self._database.find_user_by(email=email)
        except NoResultFound:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user.hashed_password)

    def create_session(self, email: str) -> str:
        """create_session function
        """
        try:
            user = self._database.find_user_by(email=email)
            session_id = generate_uuid()
            self._database.update_user(user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            return

    def get_user_from_session_id(self, session_id: str) -> str:
        """get_user_from_session_id function
        """
        if session_id is None:
            return
        try:
            user = self._database.find_user_by(session_id=session_id)
            return user.email
        except NoResultFound:
            return

    def destroy_session(self, user_id: int) -> None:
        """destroy_session function
        """
        try:
            user = self._database.find_user_by(id=user_id)
            self._database.update_user(user.id, session_id=None)
        except NoResultFound:
            pass

    def get_reset_password_token(self, email: str) -> str:
        """get_reset_password_token function
        """
        try:
            user = self._database.find_user_by(email=email)
            reset_token = generate_uuid()
            self._database.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        """update_password function
        """
        try:
            user = self._database.find_user_by(reset_token=reset_token)
            self._database.update_user(user.id,
                                       hashed_password=hash_password(password),
                                       reset_token=None)
        except NoResultFound:
            raise ValueError
