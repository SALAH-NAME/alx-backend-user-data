#!/usr/bin/env python3
""" filtered_logger.py """
from typing import List
import re
import logging
from os import environ
import mysql.connector


PERSONAL_INFO_FIELDS = ("name", "email", "phone", "ssn", "password")


def obfuscate_log_message(fields: List[str], redaction: str,
                          log_message: str, separator: str) -> str:
    """obfuscate_log_message function"""
    for field in fields:
        log_message = re.sub(f'{field}=.*?{separator}',
                             f'{field}={redaction}{separator}', log_message)
    return log_message


def create_logger() -> logging.Logger:
    """create_logger function"""
    user_logger = logging.getLogger("user_data")
    user_logger.setLevel(logging.INFO)
    user_logger.propagate = False
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(list(PERSONAL_INFO_FIELDS)))
    user_logger.addHandler(stream_handler)
    return user_logger


def connect_to_db() -> mysql.connector.connection.MySQLConnection:
    """connect_to_db function"""
    db_username = environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    db_password = environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    db_host = environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = environ.get("PERSONAL_DATA_DB_NAME")

    connection = mysql.connector.connection.MySQLConnection(
            user=db_username, password=db_password,
            host=db_host, database=db_name)
    return connection


def main():
    """main function"""
    database = connect_to_db()
    db_cursor = database.cursor()
    db_cursor.execute("SELECT * FROM users;")
    column_names = [column[0] for column in db_cursor.description]

    user_logger = create_logger()

    for row in db_cursor:
        formatted_row = ''.join(f'{column}={str(value)}; '
                                for value, column in zip(row, column_names))
        user_logger.info(formatted_row.strip())

    db_cursor.close()
    database.close()


class RedactingFormatter(logging.Formatter):
    """RedactingFormatter function"""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """__init__"""
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """format function"""
        record.msg = obfuscate_log_message(self.fields, self.REDACTION,
                                           record.getMessage(), self.SEPARATOR)
        return super(RedactingFormatter, self).format(record)


if __name__ == '__main__':
    main()
