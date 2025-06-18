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
interface=wlan0
bind-interfaces
dhcp-range=10.0.10.10,10.0.10.150,12h
port=0
no-resolv
```