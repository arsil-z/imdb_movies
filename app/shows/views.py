import uuid
import logging

from flask import request
from flask.views import MethodView


from app.auth.auth_middleware import authorize
from app.files.model import FileStatus, Files
from app.files.uploader import FileUploader, FileUploaderException
from app.files.validate import FileValidator, FileValidatorException
from app.service import response_decorator
from app.shows.model import Shows
from app.tasks.client import create_cloud_task


class ShowsUploadFileView(MethodView):

    @authorize()
    @response_decorator()
    def post(self, *args, **kwargs):

        file = request.files["file"]
        if not file:
            return {
                "message": "File missing",
                "data": None,
                "error": None
            }, 400
        logging.info(file)

        current_user = kwargs.get("current_user")

        file_name = file.filename.split(".")[0] + str(uuid.uuid4()) + ".csv"
        file_data = {
            "user_id": current_user.get("_id"),
            "status": FileStatus.INTI,
            "name": file_name
        }
        file_record = Files().create(**file_data)

        try:

            file_validator = FileValidator(file=file, file_record=file_record)
            file_record = file_validator.validate()
        except FileValidatorException as err:
            file_record = Files().update(**{
                "_id": file_record.get("_id"),
                "status": FileStatus.FAILED,
                "remarks": "Validation failed: "+str(err)
            })
            logging.error(f"File validation failed: {str(err)}")
            return {
                "message": "File validation failed",
                "data": None,
                "error": str(err)
            }, 400

        try:

            file_uploader = FileUploader(file_record=file_record)
            file_record = file_uploader.upload_file(file=file)

        except FileUploaderException as err:
            file_record = Files().update(**{
                "_id": file_record.get("_id"),
                "status": FileStatus.FAILED,
                "remarks": "Upload failed: " + str(err)
            })
            logging.error(f"File Upload failed: {str(err)}")
            return {
                "message": "File upload failed",
                "data": None,
                "error": str(err)
            }, 400

        cloud_task_data = {
            "file_record": file_record,
        }
        create_cloud_task(method="POST", url="/api/files/process", data=cloud_task_data)
        return {"message": "success"}, 200


class ShowView(MethodView):
    @authorize()
    @response_decorator()
    def get(self, *args, **kwargs):
        try:
            page = int(request.args.get("page", 1))
            page_size = int(request.args.get("page_size", 10))
            sort_by = request.args.get("sort_by", "date_added")
            sort_order = int(request.args.get("sort_order", 1))
        except ValueError as err:
            return {"message": "failed", "data": None, "error": "invalid request arguments"}, 400

        sort_by = sort_by.lower()
        if sort_by not in {"date_added", "release_year", "duration"}:
            return {"message": "failed", "data": None, "error": "invalid request arguments"}, 400

        shows = Shows().get_paginated_shows_by_filters(
            page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order
        )

        return {"message": "fetched", "data": shows, "error": None}, 200
