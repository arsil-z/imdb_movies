import logging

from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from app.auth.auth_middleware import authorize
from app.files.job import JobHandler
from app.files.model import Files, FileStatus, Jobs, JobStatus
from app.service import response_decorator


class FileProcessorView(MethodView):
    def post(self):
        try:
            data = request.get_json()
        except BadRequest as err:
            logging.info(f"FileProcessorView: get_json failed: {str(err)}")
            return {"error": "invalid request"}, 200

        file_record = data.get("file_record", {})
        if not file_record:
            return {"error": "invalid request"}, 200

        file_id = file_record.get("_id")
        if not file_id:
            return {"error": "invalid request"}, 200

        file_record = Files().get_by_id(file_id=file_id)
        if not file_record:
            return {"error": "invalid request"}, 200

        if file_record.get("status") == FileStatus.UPLOADING:
            file_record = Files().update(_id=file_id, status=FileStatus.PROCESSING)
        else:
            return {"error": "file not in uploading status"}, 200

        job_creator = JobHandler()
        job_creator.create_jobs(file_record=file_record)

        return {"message": "success"}, 200


class JobsProcessorView(MethodView):
    def post(self):
        try:
            job_record = request.get_json()
            logging.info(f"job_record first: {job_record}")
        except BadRequest as err:
            logging.info(f"JobsProcessorView: get_json failed: {str(err)}")
            return {"error": "invalid request"}, 200

        job_id = job_record.get("_id")
        if not job_id:
            logging.info("job_id not present")
            return {"error": "invalid request"}, 200

        job_record = Jobs().get_by_id(job_id=job_id)
        if not job_record:
            logging.info("job record not found")
            return {"error": "invalid request"}, 200
        logging.info(f"job_record: {job_record}")

        if job_record.get("status") == JobStatus.INIT:
            logging.info(f"job status not in INIT, {job_record.get('status')}")
            job_record = Jobs().update(_id=job_id, status=JobStatus.PROCESSING)
        else:
            logging.info("job already processed")
            return {"error": "job already processed status"}, 200

        job_handler = JobHandler()
        job_handler.process_jobs(job_record)

        return {"message": "success"}, 200


class FileView(MethodView):
    @authorize()
    @response_decorator()
    def get(self, *args, **kwargs):

        current_user = kwargs.get("current_user")
        user_id = current_user.get("_id")

        file_records = Files().get_by_user_id(user_id=user_id)

        return {"message": "Fetched", "data": file_records, "error": None}, 200
