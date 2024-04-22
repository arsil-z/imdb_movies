"""
    token_required function for handling authentication and authorization
"""
import os
import jwt

from flask import request
from jwt import PyJWTError

from app.user.model import User


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


def authorize():

    def wrap(func):

        def inner_function(*args, **kwargs):

            token = None
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].replace("Bearer", "").strip()

            if not token:
                return {
                    "message": "Authentication Token is missing!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401

            try:
                data = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            except PyJWTError as e:
                return {
                    "message": "Something went wrong",
                    "data": None,
                    "error": str(e)
                }, 500

            current_user = User().get_by_id(data["user_id"])
            if not current_user:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401

            if not current_user.get("active"):
                return {
                    "message": "Your account has been disabled",
                    "data": None,
                    "error": "Unauthorized"
                }, 401

            kwargs["current_user"] = current_user
            return func(*args, **kwargs)

        return inner_function

    return wrap
