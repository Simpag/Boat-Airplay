from flask import Flask, render_template, jsonify
import bluetooth
import subprocess
import time
import re
import threading

app = Flask(__name__)

# Constants
print_logs = False


# Function to turn on Bluetooth
def turn_on_bluetooth() -> None:
    off = True
    while off:
        # Turn on bluetooth
        ret = subprocess.run(
            ["bluetoothctl", "power", "on"], shell=False, capture_output=True
        )

        if "succeeded" in ret.stdout.decode():
            off = False
            # Turn off discoverability
            subprocess.run(
                ["bluetoothctl", "discoverable", "off"],
                shell=False,
                capture_output=True,
            )
        else:
            time.sleep(1)


# Function to get paired device MAC addresses
def get_mac_addresses() -> list:
    # Regular expression used to grab the mac addresses
    re_string = re.compile(r"(?:[0-9a-fA-F]:?){12}")
    # Grab all of the paired devices
    ret = subprocess.run(
        ["bluetoothctl", "devices", "Paired"], shell=False, capture_output=True
    )
    # Run the regex on the output
    macs = ret.stdout.decode()
    macs = re.findall(re_string, macs)

    if print_logs:
        print("MAC addresses found: ", macs)

    return macs


# Function to attempt to connect to paired devices
def connect(addresses: list) -> bool:
    # Try to connect to any of the devices given
    for address in addresses:
        ret = subprocess.run(
            ["bluetoothctl", "connect", address], shell=False, capture_output=True
        )

        if "Connection successful" not in ret.stdout.decode():
            if print_logs:
                print(
                    "Could not connect to device: ",
                    address,
                    " stdout: ",
                    ret.stdout.decode(),
                )
            continue

        if print_logs:
            print("Connected to: ", address)

        return True

    return False


# Function to check if we are connected to a device
def check_connection() -> bool:
    # Check if we are connected
    ret = subprocess.run(
        ["bluetoothctl", "devices", "Connected"], shell=False, capture_output=True
    )
    connected = len(ret.stdout) > 0
    return connected


# Function to run the connection loop in the background
def connection_loop():
    turn_on_bluetooth()
    addresses = get_mac_addresses()

    while True:
        connected = check_connection()

        if not connected:
            connected = connect(addresses)

        if connected and print_logs:
            print("Still connected!")
        elif print_logs:
            print("Disconnected!")

        time.sleep(5)


# Function to scan for Bluetooth devices
@app.route("/scan")
def scan_bluetooth_devices():
    nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_uuids=True)
    devices = [{"name": name, "address": addr} for addr, name in nearby_devices]
    return jsonify(devices)


# Function to pair and trust a device using pybluez (instead of os.system())
def pair_and_trust_device(device_address):
    try:
        # Create a socket to interact with the Bluetooth device
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((device_address, 1))  # 1 is the RFCOMM channel
        # sock.close()

        # After successful connection, trust the device (by writing to the agent)
        bluetooth.adopt_service(device_address)  # Trust the device

        return True
    except bluetooth.btcommon.BluetoothError as e:
        return False


# Route to pair and trust a device
@app.route("/pair/<device_address>")
def pair_device(device_address):
    if pair_and_trust_device(device_address):
        return jsonify({"status": "success", "device": device_address})
    else:
        return jsonify({"status": "failed", "device": device_address})


# Route to the main page (web UI)
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    # Start the connection loop in a background thread
    threading.Thread(target=connection_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=80)  # Accessible on the Pi's IP address
