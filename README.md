# Boat-Airplay
Download and install shairport-sync airplay reciever.
Pair and trust the device before running this script.
This will automatically connect to the specified bluetooth mac-address.
Run this on startup.

# Config
Set the mac address at the top of `bluetooth_connector.py`.

# Auto-run
copy bluetooth_connector.service to `/etc/systemd/system/`, then run:

* `sudo systemctl start bluetooth_connector.service` to run the script now.
* `sudo systemctl enable bluetooth_connector.service` to set the script to run every boot.

### Notes
https://unix.stackexchange.com/questions/334386/how-to-set-up-automatic-connection-of-bluetooth-headset