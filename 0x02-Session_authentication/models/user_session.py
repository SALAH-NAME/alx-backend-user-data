#!/usr/bin/env python3
""" user_session.py """
from models.base import Base


class UserSession(Base):
    """ UserSession class """
    def __init__(self, *args: list, **kwargs: dict):
        """__init__
        """
        super().__init__(*args, **kwargs)
        self.user_id = kwargs.get('user_id')
        self.session_id = kwargs.get('session_id')
        self.created_at = datetime.now()
