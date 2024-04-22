from flask import jsonify


def response_decorator():
    def wrap(func):
        def inner_function(*args, **kwargs):

            data, status_code = func(*args, **kwargs)

            return jsonify(data), status_code

        return inner_function

    return wrap
