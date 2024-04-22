import datetime

import bson

from werkzeug.security import check_password_hash, generate_password_hash

from app.db.client import mongo_conn


class User:
    def __init__(self):
        return

    def create(self, email, password):
        user = self.get_by_email(email)
        if user:
            return

        new_user = mongo_conn.users.insert_one(
            {
                "email": email,
                "password": self.encrypt_password(password),
                "active": True,
                "created_at": str(datetime.datetime.now()),
                "updated_at": str(datetime.datetime.now())
            }
        )
        return self.get_by_id(new_user.inserted_id)

    def get_by_id(self, user_id):
        user = mongo_conn.users.find_one({"_id": bson.ObjectId(user_id), "active": True})
        if not user:
            return

        user["_id"] = str(user["_id"])
        user.pop("password")
        return user

    def get_by_email(self, email):
        user = mongo_conn.users.find_one({"email": email, "active": True})
        if not user:
            return

        user["_id"] = str(user["_id"])
        return user

    def login(self, email, password):
        user = self.get_by_email(email)
        if not user or not check_password_hash(user["password"], password):
            return
        user.pop("password")
        return user

    def encrypt_password(self, password):
        return generate_password_hash(password)
