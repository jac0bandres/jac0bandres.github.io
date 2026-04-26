Raspberry Pi 4B
	- 5V power supply
	- GPIO bands
Duet3D

[Single Board Computer (SBC) setup for Duet 3 | Duet3D Documentation](https://docs.duet3d.com/User_manual/Machine_configuration/SBC_setup)
[Raspberry Pi software – Raspberry Pi](https://www.raspberrypi.com/software/)

Internet connection is necessary to update Debian packages, configure in OS setup in RPImager.

## Setup
`nmcli`: NetworkManager client

Check available devices (should have wlan0 for wifi).
```
nmcli device
```

Static connection profile for wlan0:
```
sudo nmcli connection add type wifi ifname wlan0 con-name ap-hotspot autoconnect yes ssid Duet3D-Hotspot
```

Set static IP address:
```
sudo nmcli connection modify ap-hotspot ipv4.addresses 192.168.4.1/24 ipv4.method manual
sudo nmcli connection modify ap-hotspot ipv4.gateway 192.168.4.1
sudo nmcli connection modify ap-hotspot ipv4.dns "8.8.8.8 1.1.1.1"
```

Configure WPA2
```
sudo nmcli connection modify ap-hotspot wifi-sec.key-mgmt wpa-psk
sudo nmcli connection modify ap-hotspot wifi-sec.psk "raspberry123"
```

Turn on ap mode:
```
sudo nmcli connection modify ap-hotspot 802-11-wireless.mode ap 802-11-wireless.band bg
```

Fire it:
```
sudo nmcli connection up ap-hotspot
```

Make it persistent:
```
sudo nmcli connection modify ap-hotspot connection.autoconnect yes
```