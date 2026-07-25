import re
from typing import Callable

USERNAME_PATTERN = re.compile(r'[A-Za-z0-9_-]+')
EMAIL_PATTERN = re.compile(r'[^@]+@[^@]+\.[^@]+')

def validate_registration_form(username: str, password: str, email: str, user_exists_check: Callable) -> str:
    """
    Validates the registration form data.

    Args:
        username (str): The username provided.
        password (str): The password provided.
        email (str): The email provided.
        user_exists_check (callable): A function that takes a username and returns True if it exists.

    Returns:
        str: An error message key if validation fails, empty string otherwise.
    """
    
    if not username:
        return 'bgc.error.username_notGiven'
    elif not password:
        return 'bgc.error.password_notGiven'
    elif not email:
        return 'bgc.error.email_notGiven'
    elif not EMAIL_PATTERN.fullmatch(email):
        return 'bgc.error.email_invalidAddress'
    elif len(username) < 4:
        return 'bgc.error.username_isTooShort'
    elif len(username) > 20:
        return 'bgc.error.username_isTooLong'
    elif not USERNAME_PATTERN.fullmatch(username):
        return 'bgc.error.username_containsInvalidCharacters'
    elif user_exists_check(username):
        return 'bgc.error.account_exists'

    return ''
