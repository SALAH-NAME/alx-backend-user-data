#!/usr/bin/env python3
""" filtered_logger.py """
import re
from typing import List
import logging
import mysql.connector
import os


PERSONAL_INFO_FIELDS = ("name", "email", "password", "ssn", "phone")


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
        return obfuscate_log_message(self.fields, self.REDACTION,
                                     super().format(record), self.SEPARATOR)


def connect_to_db() -> mysql.connector.connection.MYSQLConnection:
    """connect_to_db function"""
    db_connection = mysql.connector.connect(
        user=os.getenv('PERSONAL_DATA_DB_USERNAME', 'root'),
        password=os.getenv('PERSONAL_DATA_DB_PASSWORD', ''),
        host=os.getenv('PERSONAL_DATA_DB_HOST', 'localhost'),
        database=os.getenv('PERSONAL_DATA_DB_NAME')
    )
    return db_connection


def obfuscate_log_message(fields: List[str], redaction: str, log_message: str,
                          separator: str) -> str:
    """obfuscate_log_message function"""
    for field in fields:
        log_message = re.sub(f'{field}=(.*?){separator}',
                             f'{field}={redaction}{separator}', log_message)
    return log_message


def create_logger() -> logging.Logger:
    """create_logger function"""
    user_logger = logging.getLogger("user_data")
    user_logger.setLevel(logging.INFO)
    user_logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    formatter = RedactingFormatter(list(PERSONAL_INFO_FIELDS))
    stream_handler.setFormatter(formatter)

    user_logger.addHandler(stream_handler)
    return user_logger


def main() -> None:
    """main function"""
    database = connect_to_db()
    db_cursor = database.cursor()
    db_cursor.execute("SELECT * FROM users;")

    column_names = [column[0] for column in db_cursor.description]
    user_logger = create_logger()

    for row in db_cursor:
        formatted_row = ''
        for value, column in zip(row, column_names):
            formatted_row += f'{column}={(value)}; '
        user_logger.info(formatted_row)

    db_cursor.close()
    database.close()


if __name__ == '__main__':
    """__main__"""
    main()
