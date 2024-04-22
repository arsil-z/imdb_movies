import os

SHOW_FILES_HEADERS = [
    "show_id", "type", "title", "director", "cast", "country", "date_added", "release_year", "rating",
    "duration", "listed_in", "description",
]

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
