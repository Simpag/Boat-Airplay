import subprocess
import time
import re

#mac_address = "00:6F:F2:C6:C7:00"
print_logs = False

def turn_on_bluetooth() -> None:
    off = True
    while off:
        # Turn on bluetooth
        ret = subprocess.run(["bluetoothctl", "power", "on"], shell=False, capture_output=True)

        if "succeeded" in ret.stdout.decode():
            off = False

            # Turn off discoverability
            subprocess.run(["bluetoothctl", "discoverable", "off"], shell=False, capture_output=True)
        else:
            time.sleep(1)


def get_mac_addresses() -> list:
    # Regular expression used to grab the mac addresses
    re_string = re.compile(r"(?:[0-9a-fA-F]:?){12}")

    # Grab all of the Paired devices
    ret = subprocess.run(["bluetoothctl", "devices", "Paired"], shell=False, capture_output=True)

    # Run the regex on the output
    macs = ret.stdout.decode()
    macs = re.findall(re_string, macs)

    if print_logs:
        print("MAC addresses found: ", macs)

    return macs


def connect(addresses: list) -> bool:
    # Try to connect to any of the devices given
    for address in addresses:
        ret = subprocess.run(["bluetoothctl", "connect", address], shell=False, capture_output=True)

        if "Connection successful" not in ret.stdout.decode():
            if print_logs:
                print("Could not connect to device: ", address, " stdout: ", ret.stdout.decode())
            continue

        if print_logs:
            print("Connected to: ", address)

        return True

    return False


def check_connection() -> bool:
    # Check if we are connected
    ret = subprocess.run(["bluetoothctl", "devices", "Connected"], shell=False, capture_output=True)
    #connected = mac_address in ret.stdout.decode()
    connected = len(ret.stdout) > 0
    return connected


def loop() -> None:
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


if __name__ == "__main__":
    loop()
    
