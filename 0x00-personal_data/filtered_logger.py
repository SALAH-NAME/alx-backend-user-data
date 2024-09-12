#!/usr/bin/env python3
""" filtered_logger.py """
from typing import List
import re
import logging
from os import environ
import mysql.connector


SENSITIVE_FIELDS = ("name", "email", "phone", "ssn", "password")


def mask_data(fields: List[str], mask: str,
              log_message: str, delimiter: str) -> str:
    """mask_data function
    """
    for field in fields:
        log_message = re.sub(f'{field}=.*?{delimiter}',
                             f'{field}={mask}{delimiter}', log_message)
    return log_message


def create_logger() -> logging.Logger:
    """create_logger function
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(MaskingFormatter(list(SENSITIVE_FIELDS)))
    logger.addHandler(stream_handler)

    return logger


def connect_db() -> mysql.connector.connection.MySQLConnection:
    """connect_db function
    """
    db_user = environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    db_password = environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    db_host = environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = environ.get("PERSONAL_DATA_DB_NAME")

    connection = mysql.connector.connection.MySQLConnection(
        user=db_user, password=db_password,
        host=db_host, database=db_name)
    return connection


class MaskingFormatter(logging.Formatter):
    """MaskingFormatter Class"""

    MASK = "***"
    LOG_FORMAT = ("[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: "
                  "%(message)s")
    DELIMITER = ";"

    def __init__(self, fields: List[str]):
        """__init__
        """
        super(MaskingFormatter, self).__init__(self.LOG_FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """format function
        """
        record.msg = mask_data(self.fields, self.MASK,
                               record.getMessage(), self.DELIMITER)
        return super(MaskingFormatter, self).format(record)


def main():
    """main function
    """
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    column_names = [i[0] for i in cursor.description]

    logger = create_logger()

    for row in cursor:
        log_message = ''.join(f'{column}={str(value)}; '
                              for value, column in zip(row, column_names))
        logger.info(log_message.strip())

    cursor.close()
    db.close()


if __name__ == '__main__':
    """__main__"""
    main()
