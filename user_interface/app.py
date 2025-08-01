import asyncio
import subprocess
import nmcli
import time
import re

from flask import Flask, render_template, jsonify, request, redirect


app = Flask(__name__)

# Constants
DEBUG = True
BLUETOOTH_SCAN_DURATION = 15  # Duration for Bluetooth scan in seconds


# ----------- WiFi Management ------------
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

    connected_mac, _ = _get_connected_devices()

    """async def bt_scan():
        nearby_devices = await BleakScanner.discover(timeout=8)

        if DEBUG:
            print("All devices: ", nearby_devices)

        return [
            {"name": dev.name, "address": dev.address}
            for dev in nearby_devices
            if dev
            and dev.name
            and dev.address != dev.name.replace("-", ":")
            and len(dev.name) > 0
            and dev.address != connected_mac
        ]  # if dev.details.get("props", {}).get("AddressType", "") != "random" ]

    devices = asyncio.run(bt_scan())"""

    subprocess.run(
        ["bluetoothctl", "--timeout", str(BLUETOOTH_SCAN_DURATION), "scan", "on"],
        shell=False,
        capture_output=True,
    )
    ret = subprocess.run(
        ["bluetoothctl", "devices"],
        shell=False,
        capture_output=True,
    )
    nearby_devices = ret.stdout.decode().strip().split("\n")

    devices = []
    for dev_line in nearby_devices:
        if not dev_line or not dev_line.startswith("Device "):
            continue

        # Parse the device line: "Device MAC_ADDRESS DEVICE_NAME"
        # Remove "Device " prefix and split by space
        dev_info = dev_line[7:]  # Remove "Device " prefix
        parts = dev_info.split(" ", 1)  # Split into max 2 parts: MAC and name

        if len(parts) < 2:
            continue

        address = parts[0]
        name = parts[1]

        # Skip if address equals name (no actual device name)
        if address == name or address == name.replace("-", ":"):
            continue

        # Skip if already connected to this device
        if address == connected_mac:
            continue

        # Skip if name is empty or just the MAC address format
        if len(name.strip()) == 0:
            continue

        devices.append({"name": name, "address": address})

    if DEBUG:
        print("All devices: ", nearby_devices)
        print("Found devices:", devices)

    return jsonify(devices)


@app.route("/bluetooth/connected")
def connected_device():
    _, name = _get_connected_devices()

    if name != "":
        return jsonify([{"name": name}])

    return jsonify([])


@app.route("/bluetooth/disconnect")
def disconnect_device():
    success = _disconnect_device()

    return jsonify({"status": success})


# Route to pair and trust a device
@app.route("/bluetooth/connect/<device_address>")
def connect_device(device_address):
    if connect_to_device(device_address):
        return jsonify({"status": "success", "device": device_address})
    else:
        return jsonify({"status": "failed", "device": device_address})


def _disconnect_device():
    ret = subprocess.run(
        ["bluetoothctl", "disconnect"],
        shell=False,
        capture_output=True,
    )

    return "Successful disconnected" in ret.stdout.decode()


# Function to pair and trust a device using pybluez (instead of os.system())
def connect_to_device(device_address):
    if DEBUG:
        print(f"Attempting to connect to device: {device_address}")

    if _is_connected():
        _disconnect_device()
        print("Currently connected, disconnecting device")

    paired_macs = set(_get_paired_mac_addresses())

    if not device_address in paired_macs:
        paired, paired_to = _pair_device(device_address)
        if not paired:
            return False

        # Check if we tried to connect to some LE
        # devices and it changed address
        if paired_to != device_address:
            if DEBUG:
                print(
                    "Device address changed during pairing, trying to connect to new address: ",
                    paired_to,
                )
            device_address = paired_to

        time.sleep(3)

        subprocess.run(
            ["bluetoothctl", "trust", device_address],
            shell=False,
            capture_output=True,
        )

        time.sleep(3)

    ret = subprocess.run(
        ["bluetoothctl", "connect", device_address],
        shell=False,
        capture_output=True,
    )

    if "Connection successful" not in ret.stdout.decode():
        if DEBUG:
            print(
                "Could not connect to device: ",
                device_address,
                " stdout: ",
                ret.stdout.decode(),
            )
        return False

    if DEBUG:
        print("Device connected successfully!")

    return True


def _pair_device(device_address):
    """async def bt_con():
        client = BleakClient(device_address)

        try:
            await client.connect()
            if DEBUG:
                print(f"Device {device_address} paired!")
        except Exception as e:
            print(e)
            return False

        return True

    paired = asyncio.run(bt_con())"""

    ret = subprocess.run(
        ["bluetoothctl", "pair", device_address],
        shell=False,
        capture_output=True,
    )

    stdout = ret.stdout.decode()
    paired = "Pairing successful" in stdout
    # Find the device address corresponding the the paired device
    # Output looks like:
    # "Device XX:XX:XX:XX:XX:XX Paired: yes"
    paired_to = re.findall(r"Device (.*) Paired: yes", stdout)

    if not paired:
        print("Failed to pair!")
        return False, None

    return True, paired_to[0] if paired_to else device_address


def _get_paired_mac_addresses() -> list:
    # Regular expression used to grab the mac addresses
    re_string = re.compile(r"(?:[0-9a-fA-F]:?){12}")

    # Grab all of the Paired devices
    ret = subprocess.run(
        ["bluetoothctl", "devices", "Paired"],
        shell=False,
        capture_output=True,
    )

    # Run the regex on the output
    macs = ret.stdout.decode()
    macs = re.findall(re_string, macs)

    if DEBUG:
        print("MAC addresses found: ", macs)

    return macs


def _get_connected_devices() -> tuple:
    # Regular expression used to grab the mac addresses
    re_string = re.compile(r"(?:[0-9a-fA-F]:?){12} .*\n$")

    # Grab all of the connected devices
    ret = subprocess.run(
        ["bluetoothctl", "devices", "Connected"],
        shell=False,
        capture_output=True,
    )

    # Run the regex on the output
    dev = ret.stdout.decode()
    dev = re.findall(re_string, dev)

    if len(dev) == 0:
        return "", ""

    dev = dev[0].strip()
    dev = dev.split(" ")
    mac = dev.pop(0)
    dev = " ".join(dev)

    if DEBUG:
        print("Connection found: ", dev)

    return mac, dev


def _is_connected():
    # Check if we are connected
    ret = subprocess.run(
        ["bluetoothctl", "devices", "Connected"],
        shell=False,
        capture_output=True,
    )
    connected = len(ret.stdout) > 0
    return connected


# Route to the main page (web UI)
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # Start the connection loop in a background thread
    app.run(host="0.0.0.0", port=5001)  # Accessible on the Pi's IP address
