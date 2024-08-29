from flask import request, url_for, redirect

from app.api import bp
from app.extensions import db
from app.models.device import Devices

# ============================
# Device Management API Routes
# ============================

@bp.route('/device/search', methods = ['GET'])
def api_device_search():
    serial_number = request.args.get('serial_number')
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if device is None:
        return { 'data': None }

    return { 'data': device.to_dict() }

@bp.route('/device/add', methods = ['POST'])
def api_device_add():
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

@bp.route('/device/edit', methods = ['POST'])
def api_device_edit():
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

@bp.route('/device/delete', methods = ['POST'])
def api_device_delete():
    serial_number = request.form['serial_number_original']
    device = Devices.query.filter_by(serial_number = serial_number).first()

    if device is None:
        return redirect(url_for('page_device', serial_number = serial_number))
    
    if device.status == 'Provisioned':
        return redirect(url_for('page_device', serial_number = serial_number, status_code = "338502PD", norm = True))
    
    db.session.delete(device)
    db.session.commit()

    return redirect(url_for('page_devices', status_code = "338202", norm = True))

@bp.route('/devices')
def api_devices_get():
    devices = Devices.query.all()
    return { 'data': [ device.to_dict() for device in devices ] }