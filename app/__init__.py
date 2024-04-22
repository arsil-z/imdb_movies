import json
import logging
import traceback
from logging.config import dictConfig

from flask import request, current_app, Response
from werkzeug.exceptions import default_exceptions, HTTPException

from app.routes import register_routes


def setup_application(app):
    configure_container_logging()
    configure_api_logs()
    configure_error_handlers()
    register_routes(app)


def configure_container_logging():
    dictConfig({
        "version": 1,
        "formatters": {"default": {
            "format": "[%(asctime)s] %(levelname)s - %(pathname)s:%(lineno)d: %(message)s",
        }},
        "handlers": {"wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default"
        }},
        "root": {
            "level": "INFO",
            "handlers": ["wsgi"]
        }
    })
    logging.basicConfig(level=logging.DEBUG)


def configure_api_logs():
    def log_requests():
        try:
            logging.info(f">>{request}")
            logging.info(f">>Request Headers: {request.headers}")
        except Exception as err:
            logging.exception(f">>Request Error: {err}")

    def log_responses(response):
        try:
            logging.info(f">>{response}")
            logging.info(f">>Response headers: {response.headers}")
        except Exception as err:
            logging.exception(f">>Response Error: {err}")

        return response

    current_app.before_request(log_requests)
    current_app.after_request(log_responses)


def configure_error_handlers():
    for exception in default_exceptions:
        current_app.register_error_handler(exception, configure_error_handler)

    current_app.register_error_handler(Exception, configure_error_handler)


def configure_error_handler(error):
    if isinstance(error, HTTPException):
        description = error.description
        code = error.code
        name = error.name
        logging.exception(f"HTTPException occurred at app level: code - {code}, name: {name}, "
                          f"description: {description}")
    else:
        code = 500
        name = "Internal Server Error"
        logging.exception(f"Exception occurred at app level: code - {code}, name: {name}, "
                          f"description: {traceback.format_exc()}")

    response = {
        "message": name,
        "status": code,
        "error": None
    }

    headers = {
        "Content-Type": "application/json"
    }

    return Response(response=json.dumps(response), status=code, headers=headers)
