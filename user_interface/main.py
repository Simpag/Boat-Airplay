import asyncio
import bluetooth
import os
import subprocess
import threading

from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method
from dbus_next.constants import PropertyAccess
from dbus_next import Variant, BusType
from flask import Flask, render_template, jsonify, request, redirect

from bluetooth_agent import SimpleAutoAcceptAgent

app = Flask(__name__)

# Constants
DEBUG = True
WPA_SUPPLICANT_CONF = (
    "test_wpa_supplicant.conf"  # "/etc/wpa_supplicant/wpa_supplicant.conf"
)

# Global
bus: MessageBus = None
adapter_path = None


# ----------- WiFi Management ------------
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
def scan_bluetooth():
    devices = []
    adapter = bus.get_proxy_object("org.bluez", adapter_path, None).get_interface(
        "org.bluez.Adapter1"
    )

    async def discover():
        await adapter.SetDiscoveryFilter({"Transport": Variant("s", "le")})
        await adapter.StartDiscovery()
        await asyncio.sleep(5)
        await adapter.StopDiscovery()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(discover())

    # After discovery, list devices
    mngr = bus.get_proxy_object("org.bluez", "/", None).get_interface(
        "org.freedesktop.DBus.ObjectManager"
    )
    objects = loop.run_until_complete(mngr.call_get_managed_objects())

    for path, interfaces in objects.items():
        if "org.bluez.Device1" in interfaces:
            props = interfaces["org.bluez.Device1"]
            name = props.get("Name", Variant("s", "Unknown")).value
            address = props.get("Address", Variant("s", "00:00:00:00:00:00")).value
            devices.append({"name": name, "address": address})

    return jsonify(devices)


# def scan_bluetooth_devices():
#     if DEBUG:
#         print("Scanning for Bluetooth devices...")

#     nearby_devices = bluetooth.discover_devices(lookup_names=True)
#     devices = [{"name": name, "address": addr} for addr, name in nearby_devices]

#     if DEBUG:
#         print("Found devices:", devices)

#     return jsonify(devices)


# Route to pair and trust a device
@app.route("/bluetooth/connect/<device_address>")
def connect_device(device_address):
    if connect_to_device(device_address):
        return jsonify({"status": "success", "device": device_address})
    else:
        return jsonify({"status": "failed", "device": device_address})


# Function to pair and trust a device using pybluez (instead of os.system())
def connect_to_device(device_address):
    device_path = find_device_path(device_address)
    if not device_path:
        if DEBUG:
            print(f"Device {device_address} not found!")
        return False

    device = bus.get_proxy_object("org.bluez", device_path, None).get_interface(
        "org.bluez.Device1"
    )
    device_props = bus.get_proxy_object("org.bluez", device_path, None).get_interface(
        "org.freedesktop.DBus.Properties"
    )

    async def pair_trust_connect():
        try:
            paired = (await device_props.call_get("org.bluez.Device1", "Paired")).value
            if not paired:
                print(f"Pairing with {device_address}...")
                await device.Pair()
        except Exception as e:
            if DEBUG:
                print("Already paired or error during pairing:", e)

            return 1

        try:
            await device_props.call_set(
                "org.bluez.Device1", "Trusted", Variant("b", True)
            )
        except Exception as e:
            if DEBUG:
                print("Error trusting:", e)

            return 2

        try:
            print(f"Connecting to {device_address}...")
            await device.Connect()
        except Exception as e:
            if DEBUG:
                print("Error connecting:", e)

            return 3

        return 0

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(pair_trust_connect())

    if result == 0:
        return True
    
    return False


def find_device_path(device_address):
    device_address = device_address.replace(":", "_")
    return f"/org/bluez/hci0/dev_{device_address}"


# Route to the main page (web UI)
@app.route("/")
def index():
    return render_template("index.html")


async def setup_bluetooth_agent():
    global bus, adapter_path

    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    agent = SimpleAutoAcceptAgent()
    bus.export("/test/agent", agent)

    mngr = bus.get_proxy_object("org.bluez", "/", None).get_interface(
        "org.freedesktop.DBus.ObjectManager"
    )
    objects = await mngr.call_get_managed_objects()

    # Find adapter
    for path, ifaces in objects.items():
        if "org.bluez.Adapter1" in ifaces:
            adapter_path = path
            break

    adapter = bus.get_proxy_object("org.bluez", adapter_path, None).get_interface(
        "org.bluez.Adapter1"
    )
    agent_manager = bus.get_proxy_object("org.bluez", "/org/bluez", None).get_interface(
        "org.bluez.AgentManager1"
    )

    await agent_manager.RegisterAgent("/test/agent", "SimpleAutoAcceptAgent")
    await agent_manager.RequestDefaultAgent("/test/agent")
    print("Bluetooth agent registered and ready.")


def start_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_bluetooth_agent())
    loop.run_forever()


if __name__ == "__main__":
    # Start the connection loop in a background thread
    threading.Thread(target=start_asyncio_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=80)  # Accessible on the Pi's IP address
