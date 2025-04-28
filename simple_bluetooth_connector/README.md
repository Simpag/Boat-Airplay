# Bluetooth connector
Pair and trust the bluetooth device before running this script using ``bluetoothctl``.
This will automatically try to connect to paired bluetooth devices.
Run this on startup.

### Auto-run
Copy `bluetooth_connector.service` to `/etc/systemd/system/`.

To enable the service, run the following: 

* `# systemctl start bluetooth_connector.service` to run the script now.
* `# systemctl enable bluetooth_connector.service` to set the script to run every boot.