import json
import logging
import os

import grpc
from google.cloud.tasks_v2 import CloudTasksClient
from google.cloud.tasks_v2.services.cloud_tasks.transports import CloudTasksGrpcTransport

CLOUD_TASKS_HOST = os.getenv("CLOUD_TASKS_HOST")
IMDB_SERVICE_DOMAIN = os.getenv("IMDB_SERVICE_DOMAIN")


def create_cloud_task(method, url, data=None):

    client = CloudTasksClient(
        transport=CloudTasksGrpcTransport(channel=grpc.insecure_channel(CLOUD_TASKS_HOST))
    )
    parent = 'projects/imdb/locations/asia-south1'
    queue_name = parent + '/queues/imdb_movies'

    task = {
        "http_request": {
            "http_method": method, "url": f"{IMDB_SERVICE_DOMAIN}{url}",
            "headers": {"Content-type": "application/json"}
        }
    }

    if data:
        body = json.dumps(data, default=str)
        task["http_request"]["body"] = body.encode()

    logging.info(f"Creating cloud task: {task}")

    response = client.create_task(parent=queue_name, task=task)
    logging.info(f"create_cloud_task response: {response.name}")
