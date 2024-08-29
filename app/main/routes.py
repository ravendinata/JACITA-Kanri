import json

import requests
from flask import render_template, request, url_for, redirect
from sqlalchemy.sql import func

import helper.common as helper
from app.main import bp
from app.extensions import db
from app.models.device import Devices, AssignedDevices, DeviceProvisioning
from helper.status import get_status

@bp.route('/')
def index():
    count_device = db.session.query(func.count(Devices.serial_number)).scalar()
    count_assigned_device = db.session.query(func.count(AssignedDevices.transaction_id)).scalar()
    return render_template('index.html', 
                           title = 'Home', 
                           count_device = count_device, 
                           count_assigned_device = count_assigned_device)

# ============================
# Device Management Web Routes
# ============================

@bp.route('/device')
def page_device_redirect():
    return redirect(url_for('page_devices'))

@bp.route('/add_device')
def page_device_add():
    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('edit_device.html', 
                               title = 'Add New Device', 
                               status = status['status'], 
                               message = status['message'])
    
    return render_template('edit_device.html', title = 'Add New Device')

@bp.route('/device/<serial_number>')
def page_device(serial_number):
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if device is None:
        return render_template('device.html', 
                               title = 'Device', 
                               device = None, 
                               error = "No device found with the specified serial number.")

    wireless_mac = device.wireless_mac
    ethernet_mac = device.ethernet_mac

    wireless_mac_lookup = None
    ethernet_mac_lookup = None

    try:
        if wireless_mac != "":
            wmac_response = requests.get(f"https://www.macvendorlookup.com/api/v2/{wireless_mac}", timeout = 30)
            if wmac_response.status_code == 200:
                wireless_mac_lookup = json.loads(wmac_response.text)
        
        if ethernet_mac != "":
            emac_response = requests.get(f"https://www.macvendorlookup.com/api/v2/{ethernet_mac}", timeout = 30)
            print(f"Response: {emac_response.text}")
            if emac_response.status_code == 200:
                ethernet_mac_lookup = json.loads(emac_response.text)
    except Exception as e:
        print(f"ERROR/EX: {e}")

    assigned_client = "-"
    if device.status == 'Provisioned':
        assigned_client = DeviceProvisioning.query.filter_by(transacted_device = serial_number, status = "Active").first().client_email

    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('device.html', 
                               title = 'Device', 
                               device = device.to_dict(), 
                               status = status['status'], 
                               message = status['message'],
                               wmac_info = wireless_mac_lookup,
                               emac_info = ethernet_mac_lookup,
                               assigned_client = assigned_client)

    return render_template('device.html', 
                           title = 'Device', 
                           device = device.to_dict(), 
                           wmac_info = wireless_mac_lookup,
                           emac_info = ethernet_mac_lookup,
                           assigned_client = assigned_client)

@bp.route('/device/<serial_number>/edit')
def page_device_edit(serial_number):
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if device is None:
        return render_template('device.html', 
                               title = 'Edit Device', 
                               device = None, 
                               error = "No device found with the specified serial number.")
    
    return render_template('edit_device.html', 
                           title = 'Edit Device', 
                           device = device.to_dict(), 
                           edit = True)
    
@bp.route('/devices')
def page_devices():
    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('devices.html', 
                               title = 'Devices', 
                               status = status['status'], 
                               message = status['message'])
    
    return render_template('devices.html', title = 'Devices')

# =======================
# Provisioning Web Routes
# =======================

@bp.route('/provisioning')
def page_provisioning():
    count_provisioned_device = db.session.query(func.count(Devices.status)).filter(Devices.status == 'Provisioned').scalar()
    
    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('provisioning/dashboard.html', 
                               title = 'Provisioning Dashboard', 
                               count_provisioned_device = count_provisioned_device, 
                               status = status['status'], 
                               message = status['message'])
    
    return render_template('provisioning/dashboard.html', 
                           title = 'Provisioning Dashboard', 
                           count_provisioned_device = count_provisioned_device)

@bp.route('/provision_device')
def page_provision_device():
    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('provision_device.html', 
                               title = 'Provision Device', 
                               status = status['status'], 
                               message = status['message'], 
                               transaction_id = helper.generate_txn_id('DEV'))

    return render_template('provision_device.html', 
                           title = 'Provision Device', 
                           transaction_id = helper.generate_txn_id('DEV'))

@bp.route('/provisioning/assigned_devices')
def page_assigned_devices():
    return render_template('assigned_devices.html', title = 'Assigned Devices')

@bp.route('/provisioning/return_device/<transaction_id>')
def page_return_device(transaction_id):
    original_transaction = DeviceProvisioning.query.filter_by(transaction_id = transaction_id).first()

    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('return_device.html', 
                               title = 'Return Device', 
                               status = status['status'], 
                               message = status['message'])
    
    return render_template('return_device.html', 
                           title = 'Return Device', 
                           transaction_id = helper.generate_txn_id('DEV'), 
                           original_transaction = original_transaction.to_dict())

@bp.route('/provisioning/view/<transaction_id>')
def page_view_provisioned_device(transaction_id):
    transaction = DeviceProvisioning.query.filter_by(transaction_id = transaction_id).first()

    if transaction is None:
        return render_template('provisioning_view.html', 
                               title = 'View Transaction', 
                               transaction = None, 
                               error = "No transaction found with the specified transaction ID.")
    
    return render_template('provisioning_view.html', 
                           title = 'View Transaction', 
                           transaction = transaction.to_dict())

@bp.route('/provisioning/view/history')
def page_view_provisioned_device_history():
    if request.args.get('deviceID'):
        title = f"Transaction History/Log for Device ID: {request.args.get('deviceID')}"
    else:
        title = "All Transaction History/Log"

    return render_template('provisioning_history.html', title = title)

# =========================
# Network Management Routes
# =========================

@bp.route('/network')
def page_network():
    return render_template('network/dashboard.html', title = 'Network Dashboard')

# RADIUS Subroutes
@bp.route('/network/radius')
def page_radius_dashboard():
    return render_template('radius/dashboard.html', title = 'RADIUS Dashboard')

@bp.route('/network/radius/login')
def page_radius_login():
    return render_template('radius/login.html', title = 'RADIUS Login')

# ========================
# Miscellaneous Web Routes
# ========================

@bp.route('/about')
def page_about():
    return render_template('about.html', title = 'About')

@bp.route('/login')
def page_login():
    return render_template('login.html', title = 'Login')