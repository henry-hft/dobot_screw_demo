#!/bin/bash

# Ethernet configuration for the Dobot connection
ETH_INTERFACE="eth0"
DOBOT_IP="192.168.1.6"
PI_IP="192.168.1.5"

# Start of the main script
echo "Configuring Ethernet for the Dobot connection..."
sudo ip link set $ETH_INTERFACE up
sudo ip addr add $PI_IP/24 dev $ETH_INTERFACE
sudo ip route add $DOBOT_IP dev $ETH_INTERFACE

# Update package list and install required system packages
sudo apt-get update
sudo apt-get install -y libblas-dev liblapack-dev libatlas-base-dev gfortran python3-dev python3-setuptools python3-opencv python3-picamera2 python3-matplotlib

# Install Miniforge
echo "Installing Miniforge..."
sudo mkdir -p ~/miniforge3
# Download Miniforge for Raspberry Pi 64-bit (aarch64)
sudo wget https://github.com/conda-forge/miniforge/releases/download/24.9.2-0/Mambaforge-24.9.2-0-Linux-aarch64.sh -O ~/miniforge3/miniforge.sh
sudo bash ~/miniforge3/miniforge.sh -b -p ~/miniforge3
sudo rm ~/miniforge3/miniforge.sh

# Add Miniforge to PATH immediately
export PATH=~/miniforge3/bin:$PATH
    
# Initialize Conda
source ~/miniforge3/bin/activate
conda init --all
echo "Miniforge installation complete. Sourcing ~/.bashrc..."
source ~/.bashrc

# Create a new conda environment
ENV_NAME="dobot_env"
echo "Creating Miniforge environment $ENV_NAME..."
conda create -n $ENV_NAME python=3.9 -y

# Activate the conda environment
echo "Activating Miniforge environment $ENV_NAME..."
conda activate $ENV_NAME

# Install Python packages
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
