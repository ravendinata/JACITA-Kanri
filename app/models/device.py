from sqlalchemy.sql import func

from app.extensions import db

class Devices(db.Model):
    # Meta Attributes
    date_added = db.Column(db.DateTime, server_default = func.now())
    date_modified = db.Column(db.DateTime, server_default = func.now(), onupdate = func.now())

    # Device Attributes
    serial_number = db.Column(db.String(15), primary_key = True)
    brand = db.Column(db.String(75))
    model = db.Column(db.String(100))
    type = db.Column(db.String(45))
    
    # Purchase Attributes
    purchase_date = db.Column(db.Date)
    
    # Operating System Attributes
    operating_system = db.Column(db.String(45))
    
    # Processor Attributes
    cpu = db.Column(db.String(200))
    gpu = db.Column(db.String(200))
    
    # Memory Attributes
    physical_mem_type = db.Column(db.String(15))
    physical_mem_size_gb = db.Column(db.Integer)
    physical_mem_slots = db.Column(db.Integer)
    physical_mem_slots_used = db.Column(db.Integer)
    
    # Storage Attributes
    storage_type = db.Column(db.String(10))
    storage_size_gb = db.Column(db.Integer)
    
    # Display Attributes
    internal_display_type = db.Column(db.String(25))
    internal_display_size_inch = db.Column(db.Float)
    internal_display_resolution = db.Column(db.String(10))
    is_touchscreen = db.Column(db.Integer)
    
    # Network Attributes
    wireless_mac = db.Column(db.String(17))
    ethernet_mac = db.Column(db.String(17))
    
    # Kanri Attributes
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
    device_wireless_mac = db.Column(db.String(17))
    device_ethernet_mac = db.Column(db.String(17))
    assignee = db.Column(db.String(100))

    def __repr__(self):
        return f"<AssignedDevice: {self.transaction_id}>"
    
    def to_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }