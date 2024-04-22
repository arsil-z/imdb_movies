import io
import logging
import traceback

import pandas as pd
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

from app.files.constants import GCS_BUCKET_NAME
from app.files.model import Files, FileStatus


class FileUploaderException(Exception):
    pass


class FileUploader:
    def __init__(self, file_record):
        self.file_record = file_record

    def upload_file(self, file):
        self.file_record = Files().update(**{
            "_id": self.file_record.get("_id"),
            "status": FileStatus.UPLOADING
        })
        self._upload_file_to_bucket(file=file)
        return self.file_record

    def _upload_file_to_bucket(self, file):
        client = storage.Client(
            credentials=AnonymousCredentials(),
            project="test",
        )
        bucket = client.bucket(GCS_BUCKET_NAME)
        if not bucket.exists():
            bucket = client.create_bucket(GCS_BUCKET_NAME)

        blob = bucket.blob(self.file_record.get("name"))
        try:
            file_data = file.read()
            df = pd.read_csv(io.BytesIO(file_data))
            number_of_rows = df.shape[0]
            file.seek(0)
            blob.upload_from_string(file_data, client=client, content_type="text/csv")
            self.file_record = Files().update(
                _id=self.file_record.get("_id"), blob_id=blob.id, total_rows=number_of_rows
            )
        except GoogleCloudError as _:
            logging.error(f"Error while uploading file to bucket: "
                          f"file_id: {str(self.file_record['_id']), traceback.format_exc()}")
            raise FileUploaderException("File upload to GCS failed")
        return
