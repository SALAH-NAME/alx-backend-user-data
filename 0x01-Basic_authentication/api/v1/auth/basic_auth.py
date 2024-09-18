#!/usr/bin/env python3
""" basic_auth.py """

from api.v1.auth.auth import Auth
from typing import TypeVar, List
from models.user import User
import base64
import binascii


class BasicAuth(Auth):
    """ BasicAuth Class
    """

    def extract_base64_authorization_header(
            self, auth_header: str) -> str:
        """ extract_base64_authorization_header function
        """
        if (auth_header is None or
                not isinstance(auth_header, str) or
                not auth_header.startswith("Basic")):
            return None

        return auth_header[6:]

    def decode_base64_authorization_header(
            self, base64_auth_header: str) -> str:
        """ decode_base64_authorization_header function
        """
        b64_header = base64_auth_header
        if b64_header and isinstance(b64_header, str):
            try:
                encoded_bytes = b64_header.encode('utf-8')
                decoded_bytes = base64.b64decode(encoded_bytes)
                return decoded_bytes.decode('utf-8')
            except binascii.Error:
                return None

    def extract_user_credentials(
            self, decoded_auth_header: str) -> (str, str):
        """ extract_user_credentials function
        """
        decoded_str = decoded_auth_header
        if (decoded_str and isinstance(decoded_str, str) and
                ":" in decoded_str):
            credentials = decoded_str.split(":", 1)
            return (credentials[0], credentials[1])
        return (None, None)

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
        return {"email": user_email, "password": user_pwd}
