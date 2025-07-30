import nmcli


def setup_hotspot(password):
    connections = nmcli.connection()
    connections = [n.name for n in connections if n.conn_type == "wifi"]

    if "RPI-Hotspot" in connections:
        print("Hotspot already set up, returning!")
        return

    print("Setting up hotspot...")
    nmcli.device.wifi_hotspot(
        ssid="AirplayBridge",
        password=password,
        band="bg",
        con_name="RPI-Hotspot",
    )

    nmcli.connection.modify(
        "RPI-Hotspot",
        {
            "ipv4.addresses": "10.0.10.1/24",
            "ipv4.method": "manual",
            "ipv4.gateway": "",
            "ipv4.dns": "",
            "connection.autoconnect": "yes",
            "connection.autoconnect-priority": "-1",
        },
    )

    nmcli.connection.down("RPI-Hotspot")  # Apply new settings


if __name__ == "__main__":
    ans1 = "1"
    ans2 = "2"
    print("Input a password of length grater than 8")
    while ans1 != ans2 and len(ans1) < 8:
        ans1 = input("Password: ")
        ans2 = input("Confirm password: ")

    setup_hotspot(ans1)
