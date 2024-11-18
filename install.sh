#!/bin/bash

# Ethernet configuration for the Dobot connection
ETH_INTERFACE="eth0"
DOBOT_IP="192.168.1.6"
PI_IP="192.168.1.5"

# Function to check if conda is installed
function check_conda_installed() {
    if ! command -v conda &> /dev/null; then
        echo "Miniconda is not installed. Installing Miniconda..."
        install_miniconda
    else
        echo "Miniconda is already installed."
        source "$(conda info --base)/etc/profile.d/conda.sh"
    fi
}

# Function to install Miniconda
function install_miniconda() {
    MINICONDA_SCRIPT="Miniconda3-latest-Linux-x86_64.sh"
    wget https://repo.anaconda.com/miniconda/$MINICONDA_SCRIPT -O /tmp/$MINICONDA_SCRIPT
    bash /tmp/$MINICONDA_SCRIPT -b -p $HOME/miniconda3
    rm /tmp/$MINICONDA_SCRIPT
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda init
    echo "Miniconda installation complete. Please restart your shell or run 'source ~/.bashrc'."
}

# Start of the main script
echo "Configuring Ethernet for the Dobot connection..."
sudo ip link set $ETH_INTERFACE up
sudo ip addr add $PI_IP/24 dev $ETH_INTERFACE
sudo ip route add $DOBOT_IP dev $ETH_INTERFACE

# Update package list and install required system packages
sudo apt-get update
sudo apt-get install -y libblas-dev liblapack-dev libatlas-base-dev gfortran python3-dev python3-setuptools python3-opencv python3-picamera2 python3-matplotlib

# Check and install Miniconda if necessary
check_conda_installed

# Create a new conda environment
ENV_NAME="dobot_env"
echo "Creating Miniconda environment $ENV_NAME..."
conda create -n $ENV_NAME python=3.9 -y

# Activate the conda environment
echo "Activating Miniconda environment $ENV_NAME..."
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
