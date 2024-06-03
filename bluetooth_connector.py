import subprocess
import time

mac_address = ""

def connect() -> bool:
    # Turn on bluetooth
    subprocess.call(["bluetoothctl", "power", "on"], shell=True)

    # Pair device
    ret = subprocess.run(["bluetoothctl", "pair", mac_address], shell=True)
    if "Paired: yes" not in ret.stdout:
        print("Could not pair to device!")
        return False
    
    # Trust device
    subprocess.call(["bluetoothctl", "trust", mac_address], shell=True)

    # Connect device
    ret = subprocess.run(["bluetoothctl", "connect", mac_address], shell=True)
    if "Connection successful" not in ret.stdout:
        print("Could not connect to device!")
        return False
    
    return True


def check_connection() -> bool:
    # Check if we are connected
    ret = subprocess.run(["bluetoothctl", "paired-devices"])
    connected = mac_address in ret.stdout
    return connected


def loop() -> None:
    while True:
        connected = check_connection()

        if not connected:
            connected = connect()

        if not connected:
            time.sleep(5)


if __name__ == "__main__":
    loop()
