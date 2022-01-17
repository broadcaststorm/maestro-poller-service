#!/usr/bin/bash
# Primarily for local development

# Update your Anaconda environment to latest version (optional)
# conda update -n base -c defaults conda

# Build Python virtual environment for Maestro
conda create -n maestro-poller-service python~=3.9.1 -y

# Activate the environment
conda activate maestro-poller-service

# Custom webexteamssdk build
git clone https://github.com/gve-vse-tim/webexteamssdk
pushd webexteamssdk
git pull all
git checkout poller
python setup.py install
popd

# Next, dependencies needed to project setup
pip install -r requirements.txt
