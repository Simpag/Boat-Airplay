#!/bin/bash

WIFI_CHECK_ATTEMPTS=5
WIFI_CHECK_DELAY=2
HOTSPOT_INTERFACE="wlan0"

# Helper function
function log {
    echo "$(date '+%Y-%m-%d %H:%M:%S') -- $1"
}

# Turn off WiFi power saving
/sbin/iw dev $HOTSPOT_INTERFACE set power_save off

# Bring interface up
/sbin/ifconfig $HOTSPOT_INTERFACE up

# Start wpa_supplicant
/bin/systemctl start wpa_supplicant

# Stop hostapd and DHCP server if running
/bin/systemctl stop isc-dhcp-server
killall isc-dhcp-server
/bin/systemctl stop hostapd
killall hostapd

sleep 2

# Try to connect to WiFi
for i in $(seq 1 $WIFI_CHECK_ATTEMPTS); do
    log "Attempt $i: Checking for WiFi connection..."
    
    if /sbin/iw dev $HOTSPOT_INTERFACE link | grep -q 'Connected'; then
        log "Connected to WiFi network."
        /bin/systemctl start systemd-timesyncd
        exit 0
    fi

    sleep $WIFI_CHECK_DELAY
done

log "WiFi not connected. Launching Hotspot..."

# Stop wpa_supplicant if running
/bin/systemctl stop wpa_supplicant
killall wpa_supplicant

# Start hostapd and DHCP server
/usr/sbin/hostapd -B -P /run/hostapd.pid /etc/hostapd/hostapd.conf
/sbin/ip addr add 10.0.10.1/24 dev $HOTSPOT_INTERFACE
/bin/systemctl start isc-dhcp-server
