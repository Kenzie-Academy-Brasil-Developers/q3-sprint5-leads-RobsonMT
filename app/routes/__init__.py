from flask import Blueprint, Flask
from app.routes.leads_blueprint import bp as bp_leads

bp_api = Blueprint("api", __name__, url_prefix="/api")


def init_app(app: Flask):
    bp_api.register_blueprint(bp_leads)

    app.register_blueprint(bp_api)
