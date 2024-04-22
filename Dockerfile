FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install ghostscript -y

RUN pip install --upgrade pip
RUN apt-get install git -y
RUN pip install gunicorn

COPY requirements.txt /app

RUN pip install -r requirements.txt


CMD gunicorn --bind :5050 run:app --reload
