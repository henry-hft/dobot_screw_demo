#!/bin/bash

# Ethernet configuration to connect to the dobot
ETH_INTERFACE="eth0"
DOBOT_IP="192.168.1.6"
PI_IP="192.168.1.5"

echo "Configuring Ethernet for the dobot connection..."
sudo ip link set $ETH_INTERFACE up
sudo ip addr add $PI_IP/24 dev $ETH_INTERFACE

# Add route to ensure Ethernet is used only for the local connection to the dobot
sudo ip route add $DOBOT_IP dev $ETH_INTERFACE

# Update package list
sudo apt-get update

# Install required packages
sudo apt-get install -y python3-numpy
sudo apt-get install -y libblas-dev
sudo apt-get install -y liblapack-dev
sudo apt-get install -y python3-dev
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y gfortran
sudo apt-get install -y python3-setuptools
sudo apt-get install -y python3-scipy
sudo apt-get install -y python3-h5py
sudo apt-get install -y python3-opencv
sudo apt-get install -y python3-virtualenv
sudo apt-get install -y python3-picamera2

# Create virtual environment
python3 -m venv dobot
source dobot/bin/activate

# Install Python packages via pip
pip install --upgrade scipy
pip install --upgrade cython
pip install tensorflow
pip install keras
pip install opencv-python
pip install flask
pip install matplotlib
pip install imutils
