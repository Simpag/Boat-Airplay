import subprocess
import time

mac_address = "04:FE:A1:71:A7:57"
print_logs = True

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

def connect() -> bool:
    # Connect device
    ret = subprocess.run(["bluetoothctl", "connect", mac_address], shell=False, capture_output=True)

    if "Connection successful" not in ret.stdout.decode():
        if print_logs:
            print("Could not connect to device!", ret.stdout.decode())
        return False

    if print_logs:
        print("Connected!")
    
    return True


def check_connection() -> bool:
    # Check if we are connected
    ret = subprocess.run(["bluetoothctl", "devices", "Connected"], shell=False, capture_output=True)
    connected = mac_address in ret.stdout.decode()
    return connected


def loop() -> None:
    while True:
        turn_on_bluetooth()
        connected = check_connection()

        if not connected:
            connected = connect()

        if connected and print_logs:
            print("Still connected!")
        elif print_logs:
            print("Disconnected!")

        time.sleep(5)


if __name__ == "__main__":
    loop()
