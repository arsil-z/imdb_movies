import logging
import traceback

import pandas as pd

from app.files.constants import SHOW_FILES_HEADERS
from app.files.model import Files, FileStatus


class FileValidatorException(Exception):
    pass


class FileValidator:

    def __init__(self, file, file_record):
        self.file = file
        self.file_record = file_record

    def validate(self):
        self.file_record = Files().update(**{
            "_id": self.file_record.get("_id"),
            "status": FileStatus.VALIDATING
        })
        self._validate_extension()
        self._validate_headers()
        return self.file_record

    def _validate_extension(self):
        file_name = self.file.filename
        file_extension = file_name.split(".")[-1]
        if file_extension != "csv":
            raise FileValidatorException("Invalid extension")
        return

    def _validate_headers(self):
        try:
            file_headers = pd.read_csv(self.file, nrows=1)
            file_headers = list(file_headers)
            if file_headers != SHOW_FILES_HEADERS:
                raise FileValidatorException("Invalid headers")
            self.file.seek(0)
        except (TypeError, StopIteration) as err:
            logging.error(traceback.format_exc())
            raise FileValidatorException("Invalid or empty file")
