import re


class UserValidator:
    def __init__(self):
        pass

    def validate_user(self, **kwargs):
        if not kwargs.get("email") or not kwargs.get("password"):
            return False, {
                "email": "Email is required",
                "password": "Password is required",
            }

        if not self.__validate_email(kwargs.get("email")):
            return False, {
                "email": "Email is invalid"
            }

        if not self.__validate_password(kwargs.get("password")):
            return False, {
                "password": "Password is invalid, Should be at least 8 characters with one letter and one number"
            }

        return True, {}

    def __validate_password(self, password: str):
        regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        return self.__validate_regex(password, regex)

    def __validate_email(self, email: str):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return self.__validate_regex(email, regex)

    def __validate_regex(self, data, regex):
        return True if re.match(regex, data) else False
