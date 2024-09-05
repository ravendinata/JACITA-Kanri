import time
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

def get_active_auth_clients():
    try:
        omada.login()
        clients = omada.getAuthorizedClients()
        
        active_clients = []
        for client in clients:
            active_clients.append(client)

        for client in active_clients:
            client['mac'] = client['mac'].replace('-', ':').lower()
    except Exception as e:
        print(e)
        active_clients = []

    return active_clients

def get_clients(columns, filter_ssid = None, format_uptime = False):
    if columns is None:
        columns = ['ip', 'ssid', 'hostName', 'networkName', 'uptime']

    try:
        omada.login()
        clients = omada.getSiteClients()
        assigned_devices = AssignedDevices.query.all()
        authenticated_clients = get_active_auth_clients()

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
            
            # Check if the client is an authenticated client
            authenticated_client = next((client for client in authenticated_clients if client['mac'] == mac), None)

            client_data['assignee'] = assigned_device.assignee if assigned_device else 'Unassigned'
            client_data['authenticated'] = authenticated_client is not None
            client_data['localUser'] = authenticated_client['localUserName'] if authenticated_client else None

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

@bp.route('/omada/authorized_clients', methods = ['GET'])
def api_omada_authorized_clients():
    try:
        data = get_active_auth_clients()
    except Exception as e:
        data = { 'error': str(e) }

    return { 'data': data }
# Daemon to keep Omada API session alive
def keep_omada_session_alive():
    while True:
        omada.login()
        print('Omada API session refreshed')

        login_status = omada.getLoginStatus()
        print(login_status)

        time.sleep(1800)

# Start the daemon
import threading
thread = threading.Thread(target = keep_omada_session_alive)
thread.start()