#!/bin/bash
# Revert Raspberry Pi din Access Point inapoi la WiFi normal
# Ruleaza: sudo bash revert_ap.sh

echo "=== Oprire si dezactivare AP ==="
sudo systemctl disable hostapd
sudo systemctl disable dnsmasq
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

echo "=== Stergere configuratie hostapd ==="
sudo rm -f /etc/hostapd/hostapd.conf

echo "=== Stergere IP static din dhcpcd.conf ==="
sudo sed -i '/interface wlan0/{N;N;d}' /etc/dhcpcd.conf

echo "=== Gata! Reboot pentru aplicare ==="
echo "Ruleaza: sudo reboot"
