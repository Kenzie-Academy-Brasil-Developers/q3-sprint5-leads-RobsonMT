from functools import wraps
from http import HTTPStatus
from typing import Callable
from flask import request

from app.exc.leads_exc import WrongKeyError
from app.exc.leads_exc import MissingKeyError

REQUIRED_FIELDS = ["name", "email", "phone"]


def validate_fields(fields: list = REQUIRED_FIELDS):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            
            missing_keys = [key for key in fields if key not in data.keys()]
            wrong_keys = [key for key in data.keys() if not key in fields]

            try:
                if wrong_keys:
                    raise WrongKeyError(
                        {
                            "expected_keys": list(fields),
                            "wrong_key(s)_sended": list(wrong_keys),
                        }
                    )
                if missing_keys:
                    raise MissingKeyError(
                        {
                            "expected_keys": list(fields),
                            "missing_key(s)": list(missing_keys),
                        }
                    )
                return func(*args, **kwargs)
            except (MissingKeyError, WrongKeyError) as e:
                return e.args[0], HTTPStatus.BAD_REQUEST

        return wrapper

    return decorator