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

### Installing drivers for usb wifi adapter (Skip this if using onboard Wi-Fi)

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

### Installing shairport-sync
Skip this section if you are building classic Shairport Sync – NQPTP is not needed for classic Shairport Sync.

```
git clone https://github.com/mikebrady/nqptp.git
cd nqptp
autoreconf -fi
./configure --with-systemd-startup
make
sudo make install
sudo systemctl enable nqptp
sudo systemctl start nqptp
cd ..
```


Download Shairport Sync, configure, compile and install it. Omit the --with-airplay-2 from the ./configure options if you are building classic Shairport Sync.

```
git clone https://github.com/mikebrady/shairport-sync.git
cd shairport-sync
autoreconf -fi
./configure --sysconfdir=/etc --with-alsa --with-soxr --with-avahi --with-ssl=openssl --with-systemd --with-airplay-2
make
sudo make install
sudo systemctl enable shairport-sync
cd ..
```

### Bluetooth audio
You must install bluez-alsa in order to pass the audio from shairport-sync to a bluetooth speaker.
```
sudo apt-get install bluez-alsa-utils
```

### Configure Shairport-Sync

Change output device to ``bluealsa`` in ``/etc/shairport-sync.conf`` under alsa config and increase `audio_backend_buffer_desired_length_in_seconds` to 0.5 seconds to prevent studders. If you wish set a `volume_max_db` if your speakers distort at high volumes. If the volume range is too large uncomment `volume_range_db`.

### Optional services
Disabling these service is optional but might reduce load on your raspberry pi:
```
sudo systemctl disable dphys-swapfile
sudo systemctl disable triggerhappy
sudo systemctl disable keyboard-setup
```

### Setting up the user interface
Follow the instructions given in `user_interface/README.md` to setup a webpage which allows you to add/remove networks and connect to bluetooth devices. This will also setup a hotspot which will be launched if no other networks are available. 

If you do not wish to use this, a simple bluetooth auto-connector script is available under `simple_bluetooth_connector/README.md`. This script will automatically try to connect to a paired bluetooth device every 5 seconds. Therefore you must manually pair and trust devices using `bluetoothctl`.

### Finishing
This optional step is applicable to a Raspberry Pi only. Run sudo raspi-config and then choose Performance Options > Overlay Filesystem and choose to enable the overlay filesystem, and to set the boot partition to be write-protected. (The idea here is that this offers more protection against files being corrupted by the sudden removal of power.)

If you want to shairport-sync to automatically restart on failure, see [here](https://ma.ttias.be/auto-restart-crashed-service-systemd/).

## Credits
Much inspiration is taken from [this](https://github.com/mikebrady/shairport-sync/blob/master/CAR%20INSTALL.md) tutorial on the shairport-sync github.

### Notes
https://unix.stackexchange.com/questions/334386/how-to-set-up-automatic-connection-of-bluetooth-headset
