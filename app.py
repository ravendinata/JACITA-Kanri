import json

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

class Devices(db.Model):
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
    is_touchscreen = db.Column(db.Boolean)
    wireless_mac = db.Column(db.String(17))
    ethernet_mac = db.Column(db.String(17))

    def __repr__(self):
        return f"<Device: {self.serial_number}>"
    
    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }
    
@app.route('/')
def page_home():
    return render_template('index.html', title = 'Home')

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

@app.route('/about')
def page_about():
    return render_template('about.html', title = 'About')

@app.route('/login')
def page_login():
    return render_template('login.html', title = 'Login')

# API Endpoints
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
    is_touchscreen = bool(request.form['is_touchscreen'])
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

    try:
        db.session.add(device)
        db.session.commit()
    except Exception as e:
        print(f"ERROR/EX: {e}")
        return redirect(url_for('page_device_add', status_code = "338500"))

    return redirect(url_for('page_device', serial_number = serial_number, status_code = "338200"))

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
    device.is_touchscreen = bool(request.form['is_touchscreen'])
    device.wireless_mac = request.form['wireless_mac']
    device.ethernet_mac = request.form['ethernet_mac']

    try:
        db.session.commit()
    except Exception as e:
        return redirect(url_for('page_device', serial_number = serial_number, status_code = "338501"))

    return redirect(url_for('page_device', serial_number = request.form['serial_number'], status_code = "338201"))

@app.route('/api/device/delete', methods = ['POST'])
def delete_device():
    serial_number = request.form['serial_number_original']
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if device is None:
        return redirect(url_for('page_device', serial_number = serial_number))
    
    db.session.delete(device)
    db.session.commit()

    return redirect(url_for('page_devices', status_code = "338202"))

@app.route('/api/devices')
def get_devices():
    devices = Devices.query.all()
    return { 'data': [ device.to_dict() for device in devices ] }


@app.route('/api/login', methods = ['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    print(f"Username: {username}")
    
    if username == 'admin' and password == 'admin':
        return redirect(url_for('page_home'))
    else:
        return redirect(url_for('page_about'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title = '404'), 404

if __name__ == '__main__':
    app.run(debug = True)