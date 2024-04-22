FROM python:3.11-slim

RUN apt-get update --no-install-recommends;
RUN pip install gcloud-tasks-emulator;

EXPOSE 8081

CMD gcloud-tasks-emulator start --port=8081 --default-queue=projects/imdb/locations/asia-south1/queues/imdb_movies --target-host=10.10.0.190 --target-port=5050
