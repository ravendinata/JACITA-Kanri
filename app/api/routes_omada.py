import urllib3

from flask import request

from app.api import bp
from app.extensions import db
from app.models.device import AssignedDevices
from helper.omada_api import Omada
from helper.common import convert_seconds_to_human_readable

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

omada = Omada("omada.cfg")
omada.login()

def get_clients(columns, filter_ssid = None, format_uptime = False):
    if columns is None:
        columns = ['ip', 'ssid', 'hostName', 'networkName', 'uptime']

    try:
        omada.login()
        clients = omada.getSiteClients()
        assigned_devices = AssignedDevices.query.all()

        # Filter clients by SSID if specified
        if filter_ssid:
            clients = [client for client in clients if 'ssid' in client]
            clients = [client for client in clients if filter_ssid in client['ssid']]
        
        # Add each client as a separate array item to the data array
        data = []
        for client in clients:
            mac = client['mac'].replace('-', ':').lower()
            client_data = { 'mac': mac }

            for column in columns:
                if column in client:
                    client_data[column] = client[column]
                else:
                    client_data[column] = None

            # Convert uptime to a human-readable format
            if 'uptime' in client_data and format_uptime:
                uptime = convert_seconds_to_human_readable(client_data['uptime'])
                client_data['uptime'] = uptime

            # Filter the pre-fetched assigned devices to find the device with the matching MAC address
            assigned_device = next((device for device in assigned_devices if device.device_wireless_mac.lower() == mac or device.device_ethernet_mac.lower() == mac), 
                                None)

            client_data['assignee'] = assigned_device.assignee if assigned_device else 'Unassigned'

            data.append(client_data)
    except Exception as e:
        print(e)
        data = []

    return data

# ================
# Omada API Routes
# ================

@bp.route('/omada/clients', methods = ['GET'])
def api_omada_clients():
    params = request.args.to_dict()
    columns = params['columns'].split(',') if 'columns' in params else None
    filter_ssid = params['filter.ssid'] if 'filter.ssid' in params else None
    format_uptime = params['format.uptime'] if 'format.uptime' in params else False

    try:
        data = get_clients(columns = columns, filter_ssid = filter_ssid, format_uptime = format_uptime)
    except Exception as e:
        data = { 'error': str(e) }

    return { 'data': data }

@bp.route('/omada/clients/raw', methods = ['GET'])
def api_omada_clients_raw():
    clients = omada.getSiteClients()

    data = []
    for client in clients:
        data.append(client)
        
    return { 'data': data }