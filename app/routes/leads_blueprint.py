from flask import Blueprint

from app.controllers import leads_controller

bp = Blueprint("leads", __name__, url_prefix="/leads")

bp.post("")(leads_controller.create_lead)
bp.get("")(leads_controller.read_leads)
bp.patch("")(leads_controller.update_lead_by_email)
bp.delete("")(leads_controller.delete_lead_by_email)
