sudo cp config/*.rules /etc/udev/rules.d

# Refresh rules
sudo udevadm control --reload-rules
