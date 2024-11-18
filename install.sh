#!/bin/bash

# Ethernet configuration for the Dobot connection
ETH_INTERFACE="eth0"
DOBOT_IP="192.168.1.6"
PI_IP="192.168.1.5"

echo "Configuring Ethernet for the Dobot connection..."
sudo ip link set $ETH_INTERFACE up
sudo ip addr add $PI_IP/24 dev $ETH_INTERFACE
sudo ip route add $DOBOT_IP dev $ETH_INTERFACE

sudo apt-get update

sudo apt-get install -y libblas-dev
sudo apt-get install -y liblapack-dev
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y gfortran
sudo apt-get install -y python3-dev
sudo apt-get install -y python3-setuptools
sudo apt-get install -y python3-opencv
sudo apt-get install -y python3-picamera2
sudo apt-get install -y python3-matplotlib

ENV_NAME="dobot_env"

echo "Creating Miniconda environment $ENV_NAME..."
conda create -n $ENV_NAME python=3.9 -y

echo "Activating Miniconda environment $ENV_NAME..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

echo "Installing Python packages..."
conda install -y numpy
conda install -y scipy
conda install -y h5py
conda install -y matplotlib
conda install -y flask
conda install -y tensorflow
conda install -y keras
conda install -y cython
conda install -y opencv
conda install -y conda-forge::imutils

echo "Setup complete. The environment $ENV_NAME is active."
echo "To activate the environment later, use: conda activate $ENV_NAME"
