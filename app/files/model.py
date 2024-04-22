import datetime
import json
import logging

import bson

from app.db.client import mongo_conn


class FileStatus:
    INTI = "init"
    VALIDATING = "validating"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    FAILED = "failed"
    SUCCESS = "success"


class Files:
    def __init__(self):
        pass

    def create(self, **kwargs):
        new_file = mongo_conn.files.insert_one(
            {
                "user_id": kwargs.get("user_id"),
                "status": kwargs.get("status", FileStatus.INTI),
                "name": kwargs.get("name"),
                "blob_id": kwargs.get("blob_id", ""),
                "progress": kwargs.get("progress", 0),
                "remarks": kwargs.get("remarks", ""),
                "total_rows": kwargs.get("total_rows", 0),
                "created_at": str(datetime.datetime.now()),
                "updated_at": str(datetime.datetime.now())
            }
        )

        return self.get_by_id(new_file.inserted_id)

    def update(self, **kwargs):
        file_id = kwargs.get("_id")
        kwargs.pop("_id")
        kwargs["updated_at"] = str(datetime.datetime.now())

        file = mongo_conn.files.update_one(
            {"_id": bson.ObjectId(file_id)},
            {
                "$set": kwargs
            }
        )
        return self.get_by_id(file_id)

    def update_progress(self, **kwargs):
        file_id = kwargs.get("_id")
        progress = kwargs.get("progress")
        kwargs.pop("_id")
        kwargs.pop("progress")

        file = mongo_conn.files.update_one(
            {"_id": bson.ObjectId(file_id)},
            {
                "$inc": {"progress": progress}
            }
        )
        return self.get_by_id(file_id)

    def get_by_id(self, file_id):
        file = mongo_conn.files.find_one({"_id": bson.ObjectId(file_id)})
        if not file:
            return

        file["_id"] = str(file["_id"])
        return file

    def get_by_user_id(self, user_id):
        user_files = []
        for file in mongo_conn.files.find({"user_id": user_id}):
            logging.info(file)
            file["_id"] = str(file["_id"])
            user_files.append(file)

        return user_files


class JobStatus:
    INIT = "init"
    PROCESSING = "processing"
    FAILED = "failed"
    SUCCESS = "success"


class Jobs:
    def __init__(self):
        pass

    def create(self, **kwargs):
        new_job = mongo_conn.jobs.insert_one(
            {
                "file_id": kwargs.get("file_id"),
                "start_row": kwargs.get("start_row"),
                "end_row": kwargs.get("end_row"),
                "status": kwargs.get("status", FileStatus.INTI),
                "remarks": kwargs.get("remarks", ""),
                "percent_work_done": kwargs.get("percent_work_done", 0.0),
                "created_at": str(datetime.datetime.now()),
                "updated_at": str(datetime.datetime.now())
            }
        )
        return self.get_by_id(new_job.inserted_id)

    def update(self, **kwargs):
        job_id = kwargs.get("_id")
        kwargs.pop("_id")

        kwargs["updated_at"] = str(datetime.datetime.now())

        job = mongo_conn.jobs.update_one(
            {"_id": bson.ObjectId(job_id)},
            {
                "$set": kwargs
            }
        )
        return self.get_by_id(job_id)

    def get_by_id(self, job_id):
        job = mongo_conn.jobs.find_one({"_id": bson.ObjectId(job_id)})
        if not job:
            return

        job["_id"] = str(job["_id"])
        return job
