from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import routes_device, routes_provisioning, routes_radius, routes_omada, routes_auth