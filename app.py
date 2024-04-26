import json
import uuid

from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from helpers.status import get_status

# Read username and password from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

    db_username = config['db_username']
    db_password = config['db_password']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_username}:{db_password}@jacita-itam-jacita.a.aivencloud.com:23758/device-inventory?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app, engine_options = { 'pool_recycle': 3600 })

# ==============================
# MODELS
# ==============================
class Devices(db.Model):
    date_added = db.Column(db.DateTime, server_default = func.now())
    date_modified = db.Column(db.DateTime, server_default = func.now(), onupdate = func.now())
    serial_number = db.Column(db.String(15), primary_key = True)
    brand = db.Column(db.String(75))
    model = db.Column(db.String(100))
    type = db.Column(db.String(45))
    purchase_date = db.Column(db.Date)
    operating_system = db.Column(db.String(45))
    cpu = db.Column(db.String(200))
    gpu = db.Column(db.String(200))
    physical_mem_type = db.Column(db.String(15))
    physical_mem_size_gb = db.Column(db.Integer)
    physical_mem_slots = db.Column(db.Integer)
    physical_mem_slots_used = db.Column(db.Integer)
    storage_type = db.Column(db.String(10))
    storage_size_gb = db.Column(db.Integer)
    internal_display_type = db.Column(db.String(25))
    internal_display_size_inch = db.Column(db.Float)
    internal_display_resolution = db.Column(db.String(10))
    is_touchscreen = db.Column(db.Integer)
    wireless_mac = db.Column(db.String(17))
    ethernet_mac = db.Column(db.String(17))
    status = db.Column(db.String(45), default = 'Unassigned')

    def __repr__(self):
        return f"<Device: {self.serial_number}>"
    
    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }
    
class DeviceProvisioning(db.Model):
    transaction_id = db.Column(db.String(20), primary_key = True)
    transaction_type = db.Column(db.String(45))
    transaction_date = db.Column(db.DateTime, server_default = func.now())
    transacted_device = db.Column(db.String(15), db.ForeignKey('devices.serial_number'))
    status = db.Column(db.String(45))
    client_email = db.Column(db.String(100))
    is_self_transaction = db.Column(db.Integer)
    officer_email = db.Column(db.String(100))
    prev_transaction_id = db.Column(db.String(20), db.ForeignKey('device_provisioning.transaction_id'))

    def __repr__(self):
        return f"<DeviceProvisioning: {self.transaction_id}>"
    
    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }
    
class AssignedDevices(db.Model):
    transaction_id = db.Column(db.String(20), primary_key = True)
    transaction_date = db.Column(db.DateTime)
    device_serial_number = db.Column(db.String(15), db.ForeignKey('devices.serial_number'))
    assignee = db.Column(db.String(100))

    def __repr__(self):
        return f"<AssignedDevice: {self.transaction_id}>"
    
    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }
    
# ==============================
# METHODS
# ==============================
    
def generate_txn_id(category: str):
    return f"{category}-{str(uuid.uuid4())[:16].upper()}"

# ==============================
# WEB ROUTES
# ==============================
@app.route('/')
def page_home():
    count_device = db.session.query(func.count(Devices.serial_number)).scalar()
    count_assigned_device = db.session.query(func.count(AssignedDevices.transaction_id)).scalar()
    return render_template('index.html', title = 'Home', count_device = count_device, count_assigned_device = count_assigned_device)

@app.route('/device')
def page_device_redirect():
    return redirect(url_for('page_devices'))

@app.route('/add_device')
def page_device_add():
    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('edit_device.html', title = 'Add New Device', status = status['status'], message = status['message'])
    
    return render_template('edit_device.html', title = 'Add New Device')

@app.route('/device/<serial_number>')
def page_device(serial_number):
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('device.html', title = 'Device', device = device.to_dict(), status = status['status'], message = status['message'])

    if device is None:
        return render_template('device.html', title = 'Device', device = None, error = "No device found with the specified serial number.")
    
    return render_template('device.html', title = 'Device', device = device.to_dict())

@app.route('/device/<serial_number>/edit')
def page_device_edit(serial_number):
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if device is None:
        return render_template('device.html', title = 'Edit Device', device = None, error = "No device found with the specified serial number.")
    
    return render_template('edit_device.html', title = 'Edit Device', device = device.to_dict(), edit = True)
    
@app.route('/devices')
def page_devices():
    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('devices.html', title = 'Devices', status = status['status'], message = status['message'])
    
    return render_template('devices.html', title = 'Devices')

@app.route('/provision_device')
def page_provision_device():
    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('provision_device.html', title = 'Provision Device', status = status['status'], message = status['message'], transaction_id = generate_txn_id('DEV'))

    return render_template('provision_device.html', title = 'Provision Device', transaction_id = generate_txn_id('DEV'))

@app.route('/provisioning/assigned_devices')
def page_assigned_devices():
    return render_template('assigned_devices.html', title = 'Assigned Devices')

@app.route('/provisioning/return_device/<transaction_id>')
def page_return_device(transaction_id):
    original_transaction = DeviceProvisioning.query.filter_by(transaction_id = transaction_id).first()

    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('return_device.html', title = 'Return Device', status = status['status'], message = status['message'])
    
    return render_template('return_device.html', title = 'Return Device', transaction_id = generate_txn_id('DEV'), original_transaction = original_transaction.to_dict())

@app.route('/provisioning/view/<transaction_id>')
def page_view_provisioned_device(transaction_id):
    transaction = DeviceProvisioning.query.filter_by(transaction_id = transaction_id).first()

    if transaction is None:
        return render_template('provisioning_view.html', title = 'View Transaction', transaction = None, error = "No transaction found with the specified transaction ID.")
    
    return render_template('provisioning_view.html', title = 'View Transaction', transaction = transaction.to_dict())

@app.route('/provisioning/view/history', methods = ['GET'])
def page_view_provisioned_device_history():
    if request.args.get('deviceID'):
        title = f"Transaction History/Log for Device ID: {request.args.get('deviceID')}"
    else:
        title = "All Transaction History/Log"

    return render_template('provisioning_history.html', title = title)

@app.route('/provisioning_dashboard')
def page_provisioning_dashboard():
    count_provisioned_device = db.session.query(func.count(Devices.status)).filter(Devices.status == 'Provisioned').scalar()
    
    if request.args.get('status_code'):
        status = get_status(request.args.get('status_code'))
        return render_template('provisioning_dashboard.html', title = 'Provisioning Dashboard', count_provisioned_device = count_provisioned_device, status = status['status'], message = status['message'])
    
    return render_template('provisioning_dashboard.html', title = 'Provisioning Dashboard', count_provisioned_device = count_provisioned_device)

@app.route('/about')
def page_about():
    return render_template('about.html', title = 'About')

@app.route('/login')
def page_login():
    return render_template('login.html', title = 'Login')

# ==============================
# API ENDPOINTS
# ==============================
@app.route('/api/device/search', methods = ['GET'])
def search_devices():
    serial_number = request.args.get('serial_number')
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if device is None:
        return { 'data': None }

    return { 'data': device.to_dict() }

@app.route('/api/device/add', methods = ['POST'])
def add_device():
    print(request.form)
    
    serial_number = request.form['serial_number']
    brand = request.form['brand']
    model = request.form['model']
    type = request.form['type']
    purchase_date = request.form['purchase_date']
    operating_system = request.form['operating_system']
    cpu = request.form['cpu']
    gpu = request.form['gpu']
    physical_mem_type = request.form['physical_mem_type']
    physical_mem_size_gb = request.form['physical_mem_size_gb']
    physical_mem_slots = request.form['physical_mem_slots']
    physical_mem_slots_used = request.form['physical_mem_slots_used']
    storage_type = request.form['storage_type']
    storage_size_gb = request.form['storage_size_gb']
    internal_display_type = request.form['internal_display_type']
    internal_display_size_inch = request.form['internal_display_size_inch']
    internal_display_resolution_w = request.form['internal_display_resolution_w']
    internal_display_resolution_h = request.form['internal_display_resolution_h']
    is_touchscreen = request.form['is_touchscreen']
    wireless_mac = request.form['wireless_mac']
    ethernet_mac = request.form['ethernet_mac']

    internal_display_resolution = f"{internal_display_resolution_w}x{internal_display_resolution_h}"

    device = Devices(serial_number = serial_number, 
                     brand = brand, model = model, type = type, 
                     purchase_date = purchase_date, 
                     operating_system = operating_system, 
                     cpu = cpu, gpu = gpu, 
                     physical_mem_type = physical_mem_type, physical_mem_size_gb = physical_mem_size_gb, 
                     physical_mem_slots = physical_mem_slots, physical_mem_slots_used = physical_mem_slots_used, 
                     storage_type = storage_type, storage_size_gb = storage_size_gb, 
                     internal_display_type = internal_display_type, internal_display_size_inch = internal_display_size_inch, 
                     internal_display_resolution = internal_display_resolution, is_touchscreen = is_touchscreen, 
                     wireless_mac = wireless_mac, ethernet_mac = ethernet_mac)
    
    if Devices.query.filter_by(serial_number = serial_number).first() is not None:
        return redirect(url_for('page_device_add', status_code = "338500E", norm = True))

    try:
        db.session.add(device)
        db.session.commit()
    except Exception as e:
        print(f"ERROR/EX: {e}")
        return redirect(url_for('page_device_add', status_code = "338500", norm = True))

    return redirect(url_for('page_device', serial_number = serial_number, status_code = "338200", norm = True))

@app.route('/api/device/edit', methods = ['POST'])
def edit_device():
    print(request.form)
    print(f"Edit device: {request.form['serial_number_original']}")
    serial_number = request.form['serial_number_original']
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if device is None:
        return redirect(url_for('page_device', serial_number = serial_number))
    
    device.serial_number = request.form['serial_number']
    device.brand = request.form['brand']
    device.model = request.form['model']
    device.type = request.form['type']
    device.purchase_date = request.form['purchase_date']
    device.operating_system = request.form['operating_system']
    device.cpu = request.form['cpu']
    device.gpu = request.form['gpu']
    device.physical_mem_type = request.form['physical_mem_type']
    device.physical_mem_size_gb = request.form['physical_mem_size_gb']
    device.physical_mem_slots = request.form['physical_mem_slots']
    device.physical_mem_slots_used = request.form['physical_mem_slots_used']
    device.storage_type = request.form['storage_type']
    device.storage_size_gb = request.form['storage_size_gb']
    device.internal_display_type = request.form['internal_display_type']
    device.internal_display_size_inch = request.form['internal_display_size_inch']
    internal_display_resolution_w = request.form['internal_display_resolution_w']
    internal_display_resolution_h = request.form['internal_display_resolution_h']
    device.internal_display_resolution = f"{internal_display_resolution_w}x{internal_display_resolution_h}"
    device.is_touchscreen = request.form['is_touchscreen']
    device.wireless_mac = request.form['wireless_mac']
    device.ethernet_mac = request.form['ethernet_mac']

    try:
        db.session.commit()
    except Exception as e:
        print(f"ERROR/EX: {e}")
        return redirect(url_for('page_device', serial_number = serial_number, status_code = "338501", norm = True))

    return redirect(url_for('page_device', serial_number = request.form['serial_number'], status_code = "338201", norm = True))

@app.route('/api/device/delete', methods = ['POST'])
def delete_device():
    serial_number = request.form['serial_number_original']
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if device is None:
        return redirect(url_for('page_device', serial_number = serial_number))
    
    if device.status == 'Provisioned':
        return redirect(url_for('page_device', serial_number = serial_number, status_code = "338502PD", norm = True))
    
    db.session.delete(device)
    db.session.commit()

    return redirect(url_for('page_devices', status_code = "338202", norm = True))

@app.route('/api/devices')
def get_devices():
    devices = Devices.query.all()
    return { 'data': [ device.to_dict() for device in devices ] }

@app.route('/api/provisioning/assigned_devices', methods = ['GET'])
def list_provisioned_devices():
    assigned_devices = db.session.query(AssignedDevices)
    return { 'data': [ txn.to_dict() for txn in assigned_devices ] }

@app.route('/api/provisioning/transactions', methods = ['GET'])
def list_provisioning_transactions():
    transactions = db.session.query(DeviceProvisioning)
    return { 'data': [ txn.to_dict() for txn in transactions ] }

@app.route('/api/provisioning/device/add', methods = ['POST'])
def provision_device():
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

@app.route('/api/provisioning/device/return', methods = ['POST'])
def return_device():
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

@app.route('/api/login', methods = ['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    print(f"Username: {username}")
    
    if username == 'admin' and password == 'admin':
        return redirect(url_for('page_home'))
    else:
        return redirect(url_for('page_about'))

# ==============================
# Error handlers
# ==============================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title = '404'), 404

if __name__ == '__main__':
    app.run(debug = True)