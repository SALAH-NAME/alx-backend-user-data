#!/usr/bin/env python3
""" auth.py """
import bcrypt
from uuid import uuid4
from typing import Union
from sqlalchemy.orm.exc import NoResultFound
from db import DB
from user import User


def hash_password(password: str) -> bytes:
    """hash_password function
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def generate_uuid() -> str:
    """generate_uuid function
    """
    return str(uuid4())


class Auth:
    """Auth class"""
    def __init__(self):
        """__init__
        """
        self.db_instance = DB()

    def register_user(self, email: str, password: str) -> User:
        """register_user function
        """
        try:
            self.db_instance.find_user_by(email=email)
        except NoResultFound:
            return self.db_instance.add_user(email, hash_password(password))
        raise ValueError("User {} already exists".format(email))

    def valid_login(self, email: str, password: str) -> bool:
        """valid_login function
        """
        user = None
        try:
            user = self.db_instance.find_user_by(email=email)
            if user is not None:
                return bcrypt.checkpw(
                    password.encode("utf-8"),
                    user.hashed_password,
                )
        except NoResultFound:
            return False
        return False

    def create_session(self, email: str) -> str:
        """create_session function
        """
        user = None
        try:
            user = self.db_instance.find_user_by(email=email)
        except NoResultFound:
            return None
        if user is None:
            return None
        session_id = generate_uuid()
        self.db_instance.update_user(user.id, session_id=session_id)
        return session_id

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """get_reset_password_token function
        """
        user = None
        if session_id is None:
            return None
        try:
            user = self.db_instance.find_user_by(session_id=session_id)
        except NoResultFound:
            return None
        return user

    def destroy_session(self, user_id: int) -> None:
        """destroy_session function
        """
        if user_id is None:
            return None
        self.db_instance.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """get_reset_password_token function
        """
        user = None
        try:
            user = self.db_instance.find_user_by(email=email)
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError()
        reset_token = generate_uuid()
        self.db_instance.update_user(user.id, reset_token=reset_token)
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """update_password function
        """
        user = None
        try:
            user = self.db_instance.find_user_by(reset_token=reset_token)
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError()
        new_password_hash = hash_password(password)
        self.db_instance.update_user(
            user.id,
            hashed_password=new_password_hash,
            reset_token=None,
        )
