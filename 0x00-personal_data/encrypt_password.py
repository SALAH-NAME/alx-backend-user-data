#!/usr/bin/env python3
""" encrypt_password.py """
import bcrypt


def generate_hashed_password(plain_password: str) -> bytes:
    """generate_hashed_password function"""
    encoded_password = plain_password.encode()
    salted_hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())

    return salted_hashed_password


def verify_password(stored_hashed_password: bytes, password: str) -> bool:
    """verify_password function"""
    is_match = False
    encoded_input_password = password.encode()
    if bcrypt.checkpw(encoded_input_password, stored_hashed_password):
        is_match = True
    return is_match
