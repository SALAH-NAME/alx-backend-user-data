#!/usr/bin/env python3
""" db.py """
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from user import Base, User
from typing import TypeVar


VALID_USER_FIELDS = [
    'id', 'email', 'hashed_password', 'session_id', 'reset_token']


class DB:
    """
    DB class
    """

    def __init__(self):
        """__init__
        """
        self._db_engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._db_engine)
        Base.metadata.create_all(self._db_engine)
        self.__db_session = None

    @property
    def _session(self):
        """_session function
        """
        if self.__db_session is None:
            DBSession = sessionmaker(bind=self._db_engine)
            self.__db_session = DBSession()
        return self.__db_session

    def add_user(self, email: str, hashed_password: str) -> User:
        """add_user function
        """
        if not email or not hashed_password:
            return
        new_user = User(email=email, hashed_password=hashed_password)
        session = self._session
        session.add(new_user)
        session.commit()
        return new_user

    def find_user_by(self, **kwargs) -> User:
        """find_user_by function
        """
        if not kwargs or any(
                field not in VALID_USER_FIELDS for field in kwargs):
            raise InvalidRequestError
        session = self._session
        try:
            return session.query(User).filter_by(**kwargs).one()
        except Exception:
            raise NoResultFound

    def update_user(self, user_id: int, **kwargs) -> None:
        """update_user function
        """
        session = self._session
        user = self.find_user_by(id=user_id)
        for key, value in kwargs.items():
            if key not in VALID_USER_FIELDS:
                raise ValueError
            setattr(user, key, value)
        session.commit()
