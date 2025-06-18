# 
## Description
A user interface for adding new wifi networks and pairing with bluetooth devices

## Dependencies
You must install the following packages on the Pi
```
# apt-get install libbluetooth-dev
```

## Installation
Must install dnsmasq:
```
sudo apt-get install dnsmasq
```

Edit the config for dnsmasq ``/etc/dnsmasq.conf``:
```
bind-interfaces
dhcp-range=10.0.10.10,10.0.10.150,12h
port=0
no-resolv
```

Create a python virtual env and install all required python packages:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

Setup hotspot to be active if no other networks are available:
```
python setup_hotspot.py
```

### Auto-run
Copy `airplay-bridge-ui.service` to `/etc/systemd/system/`.

``
sudo cp airplay-bridge-ui.service /etc/systemd/system/
``

To enable the service, run the following: 

* `sudo systemctl start airplay-bridge-ui.service` to run the script now.
* `sudo systemctl enable airplay-bridge-ui.service` to set the script to run every boot.