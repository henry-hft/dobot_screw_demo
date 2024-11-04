#!/bin/bash

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

# Install Python packages via pip
pip install --upgrade scipy
pip install --upgrade cython
pip install tensorflow
pip install keras
pip install opencv-python
pip install flask
pip install matplotlib
