from http import HTTPStatus
from flask import request, jsonify
import re

from datetime import datetime as dt

from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import Query

from app.decorators.validate_fields import validate_fields

from app.exc.leads_exc import EmailFormatError
from app.exc.leads_exc import EmailTypeError
from app.exc.leads_exc import PhoneFormatError
from app.exc.leads_exc import OnlyEmailError

from app.models.leads_model import Leads

from app.configs.database import db


def check_phone(data: dict):
    regex = '\([1-9]{2}\)[0-9]{5}\-[0-9]{4}'
    is_valid = re.fullmatch(regex, data["phone"])
    return bool(is_valid)


def check_email(data: dict):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    is_valid = re.fullmatch(regex, data["email"])
    return bool(is_valid)


@validate_fields()
def create_lead():
    data = request.get_json()

    try:
        if not check_phone(data):
            raise PhoneFormatError(data["phone"])

        if not check_email(data):
            raise EmailFormatError(data["email"])

        data.update({"name": data["name"].title()})

        lead = Leads(**data)

        session: Session = db.session
        session.add(lead)
        session.commit()

        return jsonify(lead), HTTPStatus.CREATED

    except IntegrityError as err:
        if "email" in err.args[0]:
            return {"error": f"Email `{lead.email}` already exists"}, HTTPStatus.CONFLICT
        if "phone" in err.args[0]:
            return {"error": f"Phone `{lead.phone}` already exists"}, HTTPStatus.CONFLICT
    except PhoneFormatError as err:
        return {"error": f"Phone format `{err}` not accepted, expected format `(xx)xxxxx-xxxx`"}, HTTPStatus.UNPROCESSABLE_ENTITY
    except EmailFormatError as err:
        return {"error": f"email format `{err}` not accepted, expected format `xxxxx@xxxxxx.xxx`"}, HTTPStatus.UNPROCESSABLE_ENTITY


def read_leads():
    session: Session = db.session
    base_query: Query = session.query(Leads)

    leads = base_query.order_by(Leads.visits.desc()).all()
    
    if not leads:
        return "", HTTPStatus.NO_CONTENT

    return jsonify(leads), HTTPStatus.OK


def update_lead_by_email():
    data = request.get_json()

    session: Session = db.session
    base_query: Query = db.session.query(Leads)

    try:
        if not check_email(data):
            raise EmailFormatError(data["email"])

        for key, value in data.items():
            if key != "email":
                raise OnlyEmailError(key)  
            if type(key) != str:
                raise EmailTypeError

        lead = base_query.filter_by(email=data["email"]).one()

        data.update({"visits": lead.visits + 1})
        data.update({"last_visit": dt.now()})

        for key, value in data.items():
            setattr(lead, key, value)

        session.commit()

        return "", HTTPStatus.NO_CONTENT

    except OnlyEmailError as err:
        return {"error": f"Key `{err}` not supported,only `email` key expected"}, HTTPStatus.BAD_REQUEST
    except EmailTypeError:
        return {"error": f"The email key must be a `string`"}, HTTPStatus.UNPROCESSABLE_ENTITY
    except NoResultFound:
        return {"error": "No data with requested email found"}, HTTPStatus.NO_CONTENT
    except EmailFormatError as err:
        return {"error": f"email format `{err}` not accepted, expected format `xxxxx@xxxxxx.xxx`"}, HTTPStatus.UNPROCESSABLE_ENTITY


def delete_lead_by_email():
    data = request.get_json()

    session: Session = db.session
    base_query: Query = db.session.query(Leads)

    try:
      
        for key, value in data.items():
            if key != "email":
                raise OnlyEmailError(key)
            if type(value) != str:
                raise EmailTypeError

        lead = base_query.filter_by(email=data["email"]).one()

        session.delete(lead)
        session.commit()

        return "", HTTPStatus.NO_CONTENT
        
    except OnlyEmailError as err:
        return {"error": f"Key `{err}` not supported,only `email` key expected"}, HTTPStatus.BAD_REQUEST
    except EmailTypeError:
        return {"error": "The email key must be a `string`"}, HTTPStatus.UNPROCESSABLE_ENTITY
    except NoResultFound:
        return {"error": "No data with requested email found"}, HTTPStatus.NO_CONTENT