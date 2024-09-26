#!/usr/bin/env python3
""" db.py """
from sqlalchemy import create_engine, tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from user import Base, User


class DB:
    """DB class
    """
    def __init__(self) -> None:
        """__init__
        """
        self._db_engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._db_engine)
        Base.metadata.create_all(self._db_engine)
        self.__db_session = None

    @property
    def db_session(self) -> Session:
        """db_session function
        """
        if self.__db_session is None:
            DBSession = sessionmaker(bind=self._db_engine)
            self.__db_session = DBSession()
        return self.__db_session

    def add_user(self, email: str, hashed_password: str) -> User:
        """add_user function
        """
        try:
            new_user = User(email=email, hashed_password=hashed_password)
            self.db_session.add(new_user)
            self.db_session.commit()
        except Exception:
            self.db_session.rollback()
            new_user = None
        return new_user

    def find_user_by(self, **filters) -> User:
        """find_user_by function
        """
        fields, values = [], []
        for key, value in filters.items():
            if hasattr(User, key):
                fields.append(getattr(User, key))
                values.append(value)
            else:
                raise InvalidRequestError()
        result = self.db_session.query(User).filter(
            tuple_(*fields).in_([tuple(values)])
        ).first()
        if result is None:
            raise NoResultFound()
        return result

    def update_user(self, user_id: int, **updates) -> None:
        """update_user function
        """
        user = self.find_user_by(id=user_id)
        if user is None:
            return
        update_data = {}
        for key, value in updates.items():
            if hasattr(User, key):
                update_data[getattr(User, key)] = value
            else:
                raise ValueError()
        self.db_session.query(User).filter(User.id == user_id).update(
            update_data,
            synchronize_session=False,
        )
        self.db_session.commit()
