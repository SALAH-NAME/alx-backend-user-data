#!/usr/bin/env python3
""" auth.py """
from tabnanny import check
from flask import request
from typing import TypeVar, List


UserType = TypeVar('UserType')


class Auth:
    """ Auth class
    """

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """require_auth function
        """
        normalized_path = path
        if path is None or excluded_paths is None or len(excluded_paths) == 0:
            return True
        if path[-1] != "/":
            normalized_path += "/"
        if normalized_path in excluded_paths or path in excluded_paths:
            return False
        return True

    def authorization_header(self, request=None) -> str:
        """ authorization_header function
        """
        if request is None:
            return None
        return request.headers.get("Authorization")

    def current_user(self, request=None) -> UserType:
        """ current_user function
        """
        return None
