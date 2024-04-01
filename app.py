import os

from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

# Read username and password from config.json
import json

with open('config.json', 'r') as f:
    config = json.load(f)

    db_username = config['db_username']
    db_password = config['db_password']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_username}:{db_password}@jacita-itam-jacita.a.aivencloud.com:23758/device-inventory?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

@app.route('/device/<serial_number>', methods = ['GET'])
def page_device(serial_number):
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if device is None:
        return render_template('device.html', title = 'Device', device = None, error = "No device found with the specified serial number.")
    
    return render_template('device.html', title = 'Device', device = device.to_dict())
    
@app.route('/devices')
def page_devices():
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

if __name__ == '__main__':
    app.run(debug = True)