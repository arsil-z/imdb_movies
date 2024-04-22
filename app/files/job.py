import datetime
import logging
import os
import traceback

import pandas as pd

from app.files.model import Jobs, JobStatus, Files, FileStatus
from app.shows.model import Shows
from app.tasks.client import create_cloud_task


JOBS_BATCH_SIZE = int(os.getenv("JOBS_BATCH_SIZE"))


class JobHandler:
    def __init__(self):
        self.batch_size = JOBS_BATCH_SIZE

    def create_jobs(self, file_record):

        total_rows = file_record.get("total_rows")
        file_id = file_record.get("_id")

        if total_rows < self.batch_size:
            self._create_job_record_and_task(
                file_id=file_id, start_row=1, end_row=total_rows, percent_work_done=100
            )
            return

        no_of_jobs = total_rows // self.batch_size
        remaining_rows = total_rows % self.batch_size
        percent_work_done_by_each_job = total_rows // no_of_jobs
        percent_work_done_by_each_job = (percent_work_done_by_each_job / total_rows) * 100

        end_row = 0
        for job in range(no_of_jobs):
            start_row = end_row
            end_row += self.batch_size
            self._create_job_record_and_task(
                file_id=file_id, start_row=start_row, end_row=end_row,
                percent_work_done=percent_work_done_by_each_job
            )

        if remaining_rows:
            start_row = end_row
            end_row += remaining_rows
            self._create_job_record_and_task(
                file_id=file_id, start_row=start_row, end_row=end_row,
                percent_work_done=percent_work_done_by_each_job
            )

        return

    def _create_job_record_and_task(self, file_id, start_row, end_row, percent_work_done):
        job = Jobs().create(
            file_id=file_id, start_row=start_row, end_row=end_row, status=JobStatus.INIT,
            percent_work_done=percent_work_done
        )
        create_cloud_task("POST", "/api/files/process/jobs", data=job)
        return

    def process_jobs(self, job_record):
        job_id = job_record.get("_id")
        start_row = job_record.get("start_row")
        end_row = job_record.get("end_row")

        file_record = Files().get_by_id(job_record.get("file_id"))
        file_id = file_record.get("_id")
        file_name = file_record.get("name")

        # The below URL file will be changed to gs:// (google cloud storage url)
        # Since we're using the emulator we're directly pointing to docker-volumes directory
        file_data = pd.read_csv(
            f".docker-volumes/gcp-storage/IMDB_SHOWS_BUCKET/{file_name}",
            skiprows=start_row, nrows=end_row-start_row, keep_default_na=False
        )

        show_documents = self._create_show_documents(file_data=file_data, job_id=job_id)

        if show_documents:
            error = self._bulk_insert_show_documents(show_documents=show_documents)

            self._update_file_and_job_record(error=error, job_id=job_id, file_id=file_id)

        return

    def _create_show_documents(self, file_data, job_id):
        show_documents = []
        for index, row in file_data.iterrows():
            show_data = self._format_show_document(row, job_id=job_id)
            show_documents.append(show_data)
        return show_documents

    def _format_show_document(self, row, job_id):
        return {
            "show_id": row[0],
            "type": row[1],
            "title": row[2],
            "director": row[3],
            "cast": row[4].split(", ") if row[4] else [""],
            "country": row[5].split(",") if row[5] else [""],
            "date_added": row[6],
            "release_year": row[7],
            "rating": row[8],
            "duration": row[9],
            "file_duration": self._calculate_duration_in_minutes(row[9]),
            "listed_in": row[10].split(", ") if row[10] else [""],
            "description": row[11],
            "job_id": job_id,
            "created_at": str(datetime.datetime.now()),
            "updated_at": str(datetime.datetime.now())
        }

    def _bulk_insert_show_documents(self, show_documents):
        try:
            Shows().create_bulk(show_documents)
        except Exception as err:
            logging.info(f"_bulk_insert_show_documents failed, err: {traceback.format_exc()}")
            return str(err)
        return ""

    def _update_file_and_job_record(self, error, job_id, file_id):
        if error:
            Jobs().update(_id=job_id, status=JobStatus.FAILED, remarks=error)

        else:
            job_record = Jobs().update(_id=job_id, status=JobStatus.SUCCESS)

            # Fetching file record again to get the latest progress
            file_record = Files().get_by_id(file_id=file_id)
            file_progress = file_record.get("progress")
            percent_work_done_by_job = job_record.get("percent_work_done")

            if file_progress + percent_work_done_by_job >= 100.0:
                _ = Files().update(_id=file_id, progress=100, status=FileStatus.SUCCESS)
            else:
                _ = Files().update_progress(_id=file_id, progress=percent_work_done_by_job)

    def _calculate_duration_in_minutes(self, duration):
        duration = duration.lower()
        if duration.endswith("min"):
            duration = duration.split(" ")
            return int(duration[0])

        if duration.endswith("season") or duration.endswith("seasons"):
            duration = duration.split(" ")
            return int(duration[0]) * 300
