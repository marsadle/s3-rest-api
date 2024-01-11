from flask import Flask
from flask import request

from functools import reduce
import json
import broadlink

devices = {}
sub_devices = {}

def get_devices(hub_ip):
    global devices
    global sub_devices
    device = broadlink.hello(hub_ip)
    device.auth()
    devices[hub_ip] = device
    sub_devices[hub_ip] = device.get_subdevices()

def create_resp(state,gang):
    key = None
    if gang == 1:
        key = 'pwr1'
    elif gang == 2:
        key = 'pwr2'
    elif gang == 3:
        key = 'pwr3'

    if state[key] == 1:
        return '{"is_active": "true"}'
    else:
        return '{"is_active": "false"}'

def handle_request(request, did, gang, hub_ip):
    global devices
    global app

    if not hub_ip in devices:
        get_devices(hub_ip)

    if request.method == 'POST':
        data = json.loads(request.data)
        pwr = [None, None, None, None]

        if data['active'] == "true":
            pwr[gang] = 1
        else:
            pwr[gang] = 0

        return create_resp(devices[hub_ip].set_state(did, pwr[1], pwr[2], pwr[3]), gang)

    else:
        app.logger.info("Devices")
        app.logger.info(devices)

        return create_resp(devices[hub_ip].get_state(did), gang)

def request_did(request, did, hub_ip):
    global devices
    global app

    if not hub_ip in devices:
        get_devices(hub_ip)

    app.logger.info("Devices")
    app.logger.info(devices)

    return devices[hub_ip].get_state(did)

app = Flask(__name__)

@app.route("/",methods = ['GET'])
def hello():
    global app
    global sub_devices
    hub_ip = request.args.get('hub')

    if hub_ip is not None:
        try:
            get_devices(hub_ip)

        except Exception as err:
            return str(err)

        return str(sub_devices[hub_ip])
    else:
        return str(sub_devices[hub_ip])

@app.route("/<did>/<gang>", methods = ['POST', 'GET'])
def dynamic(did, gang):
    hub_ip = request.args.get('hub')
    return handle_request(request, did, int(gang), hub_ip)

@app.route("/<did>", methods = ['GET'])
def get_did(did):
    hub_ip = request.args.get('hub')
    return request_did(request, did, hub_ip)
