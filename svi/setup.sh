#!/bin/bash

# Setups a developer environment to build svi

set -e

echo "Setting up svi..."

# Check if script is started as root
if [ "$EUID" -ne 0 ]; then
  echo "This script will attempt to install system packages using xbps-install."
  echo "You may be prompted for your password."
  SUDO="sudo"
else
  SUDO=""
fi

# Update system packages first
echo "Updating system packages..."
$SUDO xbps-install -Syu

# Install system dependencies
echo "Installing system dependencies..."
$SUDO xbps-install -Sy python3 python3-devel python3-gobject gtk4-devel python3-pip git gcc ccache patchelf pkg-config parted

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Install Python dependencies
echo "Installing Python dependencies..."
./venv/bin/pip install -r requirements.txt

echo "Setup completed successfully!"
