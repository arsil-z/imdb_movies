import logging

import jwt
from flask import request
from flask.views import MethodView
from jwt import PyJWTError

from app.auth.auth_middleware import authorize, JWT_ALGORITHM, JWT_SECRET_KEY
from app.service import response_decorator
from app.user.model import User
from app.user.validate import UserValidator


class UserView(MethodView):

    @authorize()
    @response_decorator()
    def get(self, *args, **kwargs):
        current_user = kwargs.get("current_user")

        return {
            "message": "User details fetched",
            "data": {"user": current_user},
            "error": None
        }, 200

    @response_decorator()
    def post(self):
        user = request.get_json()
        if not user:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }, 400

        is_valid, error = UserValidator().validate_user(**user)
        if not is_valid:
            return {
                "message": "Invalid data",
                "data": None,
                "error": error
            }, 400

        user = User().create(**user)
        if not user:
            return {
                "message": "User already exists",
                "data": None,
                "error": "Conflict"
            }, 409

        return {
            "message": "Successfully created new user",
            "data": user
        }, 201


class LoginView(MethodView):

    @response_decorator()
    def post(self):
        data = request.get_json()
        if not data:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }, 400

        # validate input
        is_valid, error = UserValidator().validate_user(**data)
        if is_valid is not True:
            return {
                "message": "Invalid data",
                "data": None,
                "error": error
            }, 400

        user = User().login(data["email"], data["password"])

        if user:
            try:
                # token should expire after 24 hrs
                user["token"] = jwt.encode({"user_id": user["_id"]}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
                return {
                    "message": "Successfully fetched auth token",
                    "data": user
                }, 200
            except PyJWTError as e:
                return {
                    "error": "Something went wrong",
                    "message": str(e)
                }, 500

        return {
            "message": "Error fetching auth token!, invalid email or password",
            "data": None,
            "error": "Unauthorized"
        }, 404
