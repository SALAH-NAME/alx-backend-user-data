#!/usr/bin/env python3
""" filtered_logger.py """
import re


def filter_datum(fields, redaction, message, separator):
    """filter_datum function
    """
    pattern = '|'.join([f'{field}=[^{separator}]*' for field in fields])
    return re.sub(pattern, lambda m: f"{m.group(0).split('=')[0]}={redaction}",
                  message)


class RedactingFormatter(logging.Formatter):
    """RedactingFormatter class
    """
    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields):
        """__init__
        """
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """format function
        """
        original_message = super().format(record)
        return filter_datum(self.fields, self.REDACTION, original_message,
                            self.SEPARATOR)


def get_logger() -> logging.Logger:
    """"get_logger function
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    stream_handler = logging.StreamHandler()
    formatter = RedactingFormatter(fields=PII_FIELDS)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """get_db function
    """
    username = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    password = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.getenv("PERSONAL_DATA_DB_NAME")

    return mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=db_name
    )


def main():
    """main function
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    logger = get_logger()

    for row in cursor:
        message = (
            f"name={row[0]}; email={row[1]}; phone={row[2]}; ssn={row[3]}; "
            f"password={row[4]}; ip={row[5]}; last_login={row[6]}; "
            f"user_agent={row[7]};"
        )
        log_record = logging.LogRecord(
            "user_data", logging.INFO, None, None, message, None, None
        )
        logger.handle(log_record)

    cursor.close()
    db.close()


if __name__ == "__main__":
    """__main__
    """
    main()
