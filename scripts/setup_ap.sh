#!/bin/bash
# Configureaza Raspberry Pi ca Access Point WiFi
# Ruleaza o singura data: sudo bash setup_ap.sh

SSID="DroneNet"
PASSWORD="drone1234"
PI_IP="192.168.4.1"

echo "=== Instalare pachete ==="
sudo apt update
sudo apt install -y hostapd dnsmasq

sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

echo "=== Configurare IP static pentru wlan0 ==="
sudo tee /etc/dhcpcd.conf > /dev/null <<EOF
interface wlan0
    static ip_address=${PI_IP}/24
    nohook wpa_supplicant
EOF

echo "=== Configurare DHCP server ==="
sudo tee /etc/dnsmasq.conf > /dev/null <<EOF
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF

echo "=== Configurare Access Point ==="
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<EOF
interface=wlan0
driver=nl80211
ssid=${SSID}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=${PASSWORD}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

sudo sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

echo "=== Activare servicii la boot ==="
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

echo "=== Gata! Reboot pentru aplicare ==="
echo "SSID: ${SSID}"
echo "Password: ${PASSWORD}"
echo "Pi IP: ${PI_IP}"
echo ""
echo "Ruleaza: sudo reboot"
