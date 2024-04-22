import os

from pymongo import MongoClient

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

mongo_client = MongoClient(host=MONGO_HOST,
                           port=MONGO_PORT,
                           username=MONGO_USER,
                           password=MONGO_PASSWORD,
                           authSource="admin")

mongo_conn = mongo_client.imdb_movies
