# Boat-Airplay


## Installation
Install raspberry pi os lite 64 bit for raspberry pi zero 2W.

Update raspi

```
# apt-get update
# apt-get upgrade
# rpi-update
```

Expand to full disk size, turn on auto login and update
```
# raspi-config
```

Install build toold

```
# apt install --no-install-recommends build-essential git xmltoman autoconf automake libtool libpopt-dev libconfig-dev libasound2-dev avahi-daemon libavahi-client-dev libssl-dev libsoxr-dev libplist-dev libsodium-dev libavutil-dev libavcodec-dev libavformat-dev uuid-dev libgcrypt-dev xxd
```

Install kernel headers
```
# apt install raspberrypi-kernel-headers
```

Clone [drivers](https://github.com/aircrack-ng/rtl8188eus?tab=readme-ov-file) and install
```
git clone https://github.com/aircrack-ng/rtl8188eus.git
```

Disable built in wifi by adding to ``/boot/firmware/config.txt``
```
dtoverlay=pi3-disable-wifi
```

Follow [shairport-sync tutorial](https://github.com/mikebrady/shairport-sync/blob/master/CAR%20INSTALL.md) to install shairport-sync airplay 2 and wifi hotspot

Make rc.local executable by adding ``# chmod +x /etc/rc.local``

## Bluetooth audio
```
# apt-get install bluez-alsa-utils
```

Change output device to ``bluealsa`` in ``/etc/shairport-sync.conf``

## Bluetooth connector
Pair and trust the bluetooth device before running this script using ``bluetoothctl``.
This will automatically try to connect to paired bluetooth devices.
Run this on startup.

### Auto-run
Copy `bluetooth_connector.service` to `/etc/systemd/system/`.

To enable the service, run the following: 

* `sudo systemctl start bluetooth_connector.service` to run the script now.
* `sudo systemctl enable bluetooth_connector.service` to set the script to run every boot.

## Finishing
This optional step is applicable to a Raspberry Pi only. Run sudo raspi-config and then choose Performance Options > Overlay Filesystem and choose to enable the overlay filesystem, and to set the boot partition to be write-protected. (The idea here is that this offers more protection against files being corrupted by the sudden removal of power.)

### Notes
https://unix.stackexchange.com/questions/334386/how-to-set-up-automatic-connection-of-bluetooth-headset
