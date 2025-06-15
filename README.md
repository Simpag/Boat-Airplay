# Boat-Airplay

## Hardware
* Raspberry Pi zero 2 W
* TP-Link TL-WN722N

## Installation
Install raspberry pi os lite 64 bit for raspberry pi zero 2W.

```
sudo apt-get update
sudo apt-get upgrade -y
```

Expand to full disk size, turn on auto login, set wlan country and update using:
```
sudo raspi-config
```

Install build tools

```
sudo apt install --no-install-recommends build-essential git xmltoman autoconf automake libtool libpopt-dev libconfig-dev libasound2-dev avahi-daemon libavahi-client-dev libssl-dev libsoxr-dev libplist-dev libsodium-dev libavutil-dev libavcodec-dev libavformat-dev uuid-dev libgcrypt-dev xxd bc
```

Install kernel headers
```
sudo apt install raspberrypi-kernel-headers
```

Clone [drivers](https://github.com/aircrack-ng/rtl8188eus?tab=readme-ov-file) and install according to github instructions
```
git clone https://github.com/aircrack-ng/rtl8188eus.git

cd rtl8188eus
make && sudo make install

echo 'blacklist r8188eu' | sudo tee -a '/etc/modprobe.d/realtek.conf'
echo 'blacklist rtl8xxxu' | sudo tee -a '/etc/modprobe.d/realtek.conf'
```

Disable built in wifi by adding to ``/boot/firmware/config.txt``
```
echo 'dtoverlay=pi3-disable-wifi' | sudo tee -a /boot/firmware/config.txt
```

Follow [shairport-sync tutorial](https://github.com/mikebrady/shairport-sync/blob/master/CAR%20INSTALL.md) to install shairport-sync airplay 2 and wifi hotspot

Make rc.local executable by adding ``sudo chmod +x /etc/rc.local``. Set the alsamixer output to 0db gain by adding `amixer set 'PCM',0 0db unmute` to the rc.local script.

Example hostapd config 
```
# Thanks to https://wiki.gentoo.org/wiki/Hostapd#802.11b.2Fg.2Fn_triple_AP

# The interface used by the AP
interface=wlan0

# This is the name of the network -- yours may be different
ssid=Ohana

# 1=wpa, 2=wep, 3=both
auth_algs=1

# WPA2 only
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase=somepassword

# "g" simply means 2.4GHz band
hw_mode=g

# Channel to use
channel=11

# Limit the frequencies used to those allowed in the country
ieee80211d=1

# The country code
country_code=SE

# Enable 802.11n support
ieee80211n=1

# QoS support, also required for full speed on 802.11n/ac/ax
wmm_enabled=1

```

## Bluetooth audio
```
sudo apt-get install bluez-alsa-utils
```

Change output device to ``bluealsa`` in ``/etc/shairport-sync.conf`` and increase desired buffer length to 0.4 seconds to prevent studders. 

## Finishing
This optional step is applicable to a Raspberry Pi only. Run sudo raspi-config and then choose Performance Options > Overlay Filesystem and choose to enable the overlay filesystem, and to set the boot partition to be write-protected. (The idea here is that this offers more protection against files being corrupted by the sudden removal of power.)

### Notes
https://unix.stackexchange.com/questions/334386/how-to-set-up-automatic-connection-of-bluetooth-headset
