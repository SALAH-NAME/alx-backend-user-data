#!/usr/bin/env python3
""" basic_auth.py """

from api.v1.auth.auth import Auth
from typing import TypeVar, List
from models.user import User
import base64
import binascii


UserType = TypeVar('UserType')


class BasicAuth(Auth):
    """ BasicAuth Class
    """

    def extract_base64_authorization_header(
            self, auth_header: str) -> str:
        """ extract_base64_authorization_header function
        """
        if (auth_header is None or
                not isinstance(auth_header, str) or
                not auth_header.startswith("Basic ")):
            return None

        return auth_header[6:]

    def decode_base64_authorization_header(
            self, base64_auth_header: str) -> str:
        """ decode_base64_authorization_header function
        """
        if base64_auth_header is None or not isinstance(
                base64_auth_header, str):
            return None
        try:
            decoded_bytes = base64.b64decode(
                    base64_auth_header.encode('utf-8'))
            return decoded_bytes.decode('utf-8')
        except binascii.Error:
            return None

    def extract_user_credentials(
            self, decoded_auth_header: str) -> (str, str):
        """ extract_user_credentials function
        """
        if decoded_auth_header is None or ":" not in decoded_auth_header:
            return (None, None)
        return tuple(decoded_auth_header.split(":", 1))

    def user_object_from_credentials(
            self, user_email: str, user_pwd: str) -> UserType:
        """ user_object_from_credentials function
        """
        if user_email is None or not isinstance(user_email, str):
            return None
        if user_pwd is None or not isinstance(user_pwd, str):
            return None

        users = User.search({"email": user_email})
        if not users:
            return None

        user = users[0]
        if not user.is_valid_password(user_pwd):
            return None

        return user

    def current_user(self, request=None) -> TypeVar('User'):
        """ current_user function
        """

        auth_header = self.authorization_header(request)
        if auth_header is None:
            return None
        base64_auth_header = self.extract_base64_authorization_header(
                auth_header)
        if base64_auth_header is None:
            return None
        decoded_auth_header = self.decode_base64_authorization_header(
                base64_auth_header)
        if decoded_auth_header is None:
            return None
        user_email, user_pwd = self.extract_user_credentials(
                decoded_auth_header)
        if user_email is None or user_pwd is None:
            return None
        return self.user_object_from_credentials(user_email, user_pwd)
