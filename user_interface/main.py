import asyncio
from bleak import BleakScanner, BleakClient
import subprocess

from flask import Flask, render_template, jsonify, request, redirect


app = Flask(__name__)

# Constants
DEBUG = True
WPA_SUPPLICANT_CONF = (
    "test_wpa_supplicant.conf"  # "/etc/wpa_supplicant/wpa_supplicant.conf"
)


# ----------- WiFi Management ------------
## TODO: Show currently saved WiFi networks and allow them to be removed.
@app.route("/wifi", methods=["GET", "POST"])
def wifi_setup():
    if request.method == "POST":
        ssid = request.form["ssid"]
        password = request.form["password"]
        add_wifi_network(ssid, password)
        restart_wifi_manager()
        return redirect("/")
    return render_template("wifi.html")


def add_wifi_network(ssid, password):
    network_block = f"""
network={{
    ssid="{ssid}"
    psk="{password}"
}}
"""

    if DEBUG:
        print(f"Adding network block to {WPA_SUPPLICANT_CONF}:\n{network_block}")

    with open(WPA_SUPPLICANT_CONF, "a") as f:
        f.write(network_block)


def restart_wifi_manager():
    subprocess.run(["sudo", "systemctl", "restart", "wifi-manager.service"])


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
        finally:
            await client.disconnect()
            return True

    return asyncio.run(bt_con())


# Route to the main page (web UI)
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # Start the connection loop in a background thread
    app.run(host="0.0.0.0", port=5001)  # Accessible on the Pi's IP address
