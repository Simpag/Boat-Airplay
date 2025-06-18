import asyncio
from bleak import BleakScanner, BleakClient
import subprocess
import nmcli

from flask import Flask, render_template, jsonify, request, redirect


app = Flask(__name__)

# Constants
DEBUG = True


# ----------- WiFi Management ------------
## TODO: Show currently saved WiFi networks and allow them to be removed.
@app.route("/wifi")
def wifi_setup():
    return render_template("wifi.html")


# Function to scan for wifi networks
@app.route("/wifi/scan")
def scan_wifi_networks():
    if DEBUG:
        print("Scanning for wifi networks...")

    results = nmcli.device.wifi(rescan=True)

    ssids_found = {"RPI-Hotspot"}  # Dont include itself
    devices = []
    for r in results:
        if r.ssid in ssids_found or r.ssid == "" or r.ssid == None:
            continue

        same_ssids = [rr for rr in results if rr.ssid == r.ssid]
        is_in_use = [ss for ss in same_ssids if ss.in_use]

        if len(is_in_use) == 0:
            to_show = max(same_ssids, key=lambda x: x.signal)
        else:
            to_show = is_in_use[0]

        ssids_found.add(to_show.ssid)
        devices.append(
            {
                "ssid": to_show.ssid,
                "in_use": to_show.in_use,
                "signal": to_show.signal,
            }
        )

    if DEBUG:
        print("Found devices:", devices)

    return jsonify(devices)


@app.route("/wifi/networks")
def get_saved_networks():
    connections = nmcli.connection()
    connections = [
        {"name": n.name}
        for n in connections
        if n.conn_type == "wifi" and n.name != "RPI-Hotspot"
    ]  # Dont include itself
    if DEBUG:
        print("Found connections: ", connections)

    return jsonify(connections)


# Route to pair and trust a device
@app.route("/wifi/connect", methods=["POST"])
def connect_wifi():
    """
    Body (JSON): { "ssid": "<network-name>", "password": "<secret>" }
    """
    data = request.get_json(force=True)
    ssid = data.get("ssid")
    password = data.get("password")

    if DEBUG:
        print("Trying to connect to: ", ssid, " with password: ", password)

    success = True
    try:
        nmcli.device.wifi_connect(ssid, password, "wlan0")
    except nmcli.ConnectionActivateFailedException as e:
        _remove_wifi(ssid)
        success = False

    if DEBUG:
        print("Connection result: ", {"status": success, "ssid": ssid})

    return jsonify({"status": success, "ssid": ssid})


@app.route("/wifi/remove", methods=["POST"])
def remove_wifi_network():
    data = request.get_json(force=True)
    ssid = data.get("ssid")

    if DEBUG:
        print("Trying to remove: ", ssid)

    success = _remove_wifi(ssid)

    if DEBUG:
        print("Connection result: ", {"status": success, "ssid": ssid})

    return jsonify({"status": success, "ssid": ssid})


def _remove_wifi(ssid: str):
    try:
        nmcli.connection.delete(ssid)
    except Exception as e:
        return False

    return True


# ----------- Bluetooth Management ------------
@app.route("/bluetooth")
def bluetooth_setup():
    return render_template("bluetooth.html")


# Function to scan for Bluetooth devices
@app.route("/bluetooth/scan")
def scan_bluetooth_devices():
    if DEBUG:
        print("Scanning for Bluetooth devices...")

    async def bt_scan():
        nearby_devices = await BleakScanner.discover(timeout=8)
        return [
            {"name": dev.name, "address": dev.address}
            for dev in nearby_devices
            if dev.address != dev.name.replace("-", ":")
        ]  # if dev.details.get("props", {}).get("AddressType", "") != "random" ]

    devices = asyncio.run(bt_scan())

    if DEBUG:
        print("Found devices:", devices)

    return jsonify(devices)


# Route to pair and trust a device
@app.route("/bluetooth/connect/<device_address>")
def connect_device(device_address):
    if connect_to_device(device_address):
        return jsonify({"status": "success", "device": device_address})
    else:
        return jsonify({"status": "failed", "device": device_address})


# Function to pair and trust a device using pybluez (instead of os.system())
def connect_to_device(device_address):
    if DEBUG:
        print(f"Attempting to connect to device: {device_address}")

    async def bt_con():
        client = BleakClient(device_address)

        try:
            await client.connect()
        except Exception as e:
            print(e)
            return False

        return True

    return asyncio.run(bt_con())


# Route to the main page (web UI)
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # Start the connection loop in a background thread
    app.run(host="0.0.0.0", port=5001)  # Accessible on the Pi's IP address
