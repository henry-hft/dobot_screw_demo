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
sudo apt-get install -y libcap-dev
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
sudo apt-get install -y python3-libcamera
sudo apt-get install -y python3-matplotlib
sudo apt-get install -y python3-virtualenv
sudo apt-get install -y libcap-dev
sudo apt-get install -y libatlas-base-dev 
sudo apt-get install -y ffmpeg 
sudo apt-get install -y libopenjp2-7
sudo apt-get install -y libcamera-dev
sudo apt-get install -y libkms++-dev 
sudo apt-get install -y libfmt-dev 
sudo apt-get install -y libdrm-dev


# Create virtual environment
virtualenv --system-site-packages dobot
source dobot/bin/activate

# Install Python packages via pip
python -m pip install --upgrade scipy
python -m pip install --upgrade cython
python -m pip install imutils
python -m pip install tensorflow
python -m pip install keras
python -m pip install opencv-python
python -m pip install flask
python -m pip install matplotlib
python -m pip install wheel
python -m pip install rpi-libcamera
python -m pip install rpi-kms
python -m pip install picamera2
python -m pip install numpy==1.26.4

sudo chown -R .
