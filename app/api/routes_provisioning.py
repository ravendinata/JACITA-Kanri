from flask import request, url_for, redirect

from app.api import bp
from app.extensions import db
from app.models.device import Devices, AssignedDevices, DeviceProvisioning

# =======================
# Provisioning API Routes
# =======================

@bp.route('/provisioning/assigned_devices', methods = ['GET'])
def api_assigned_devices_get():
    assigned_devices = db.session.query(AssignedDevices)
    return { 'data': [ txn.to_dict() for txn in assigned_devices ] }

@bp.route('/provisioning/transactions', methods = ['GET'])
def api_transactions_get():
    transactions = db.session.query(DeviceProvisioning)
    return { 'data': [ txn.to_dict() for txn in transactions ] }

@bp.route('/provisioning/device/add', methods = ['POST'])
def api_transaction_add():
    print(request.form)
    transaction_id = request.form['transaction_id']
    transaction_type = request.form['transaction_type']
    transacted_device = request.form['transacted_device']
    client_email = request.form['client_email']
    is_self_transaction = request.form['is_self_transaction']
    officer_email = request.form['officer_email']

    # Check if the device is already provisioned
    device = Devices.query.filter_by(serial_number = transacted_device).first()
    if device.status == 'Provisioned':
        return redirect(url_for('page_provision_device', status_code = "778500PD", norm = True))

    device_provisioning = DeviceProvisioning(transaction_id = transaction_id,
                                             transaction_type = transaction_type,
                                             transacted_device = transacted_device,
                                             status = 'Active',
                                             client_email = client_email,
                                             is_self_transaction = is_self_transaction,
                                             officer_email = officer_email)
    
    device.status = 'Provisioned'
    
    try:
        db.session.add(device_provisioning)
        db.session.commit()
    except Exception as e:
        print(f"ERROR/EX: {e}")
        return redirect(url_for('page_provision_device', status_code = "778500", norm = True))
    
    return redirect(url_for('page_provisioning_dashboard', status_code = "778200", norm = True))

@bp.route('/provisioning/device/return', methods = ['POST'])
def api_transaction_return():
    print(request.form)
    transaction_id = request.form['transaction_id']
    transacted_device = request.form['transacted_device']
    client_email = request.form['client_email']
    is_self_transaction = request.form['is_self_transaction']
    officer_email = request.form['officer_email']
    prev_transaction_id = request.form['checkout_transaction_id']

    checkout_transaction = DeviceProvisioning.query.filter_by(transaction_id = prev_transaction_id).first()
    checkout_transaction.status = 'Closed'

    device_provisioning = DeviceProvisioning(transaction_id = transaction_id,
                                             transaction_type = 'Return',
                                             transacted_device = transacted_device,
                                             client_email = client_email,
                                             is_self_transaction = is_self_transaction,
                                             officer_email = officer_email,
                                             prev_transaction_id = prev_transaction_id)
    
    device = Devices.query.filter_by(serial_number = transacted_device).first()
    device.status = "Unassigned"

    try:
        db.session.add(device_provisioning)
        db.session.commit()
    except Exception as e:
        print(f"ERROR/EX: {e}")
        return redirect(url_for('page_return_device', transaction_id = prev_transaction_id, status_code = "778500", norm = True))
    
    return redirect(url_for('page_provisioning_dashboard', status_code = "778200", norm = True))