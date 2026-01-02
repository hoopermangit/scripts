#!/bin/bash

# Downloads the latest tarball from https://codeberg.org/LinuxNation/svi/releases
# and unpacks it into /usr/local/bin/ and the .desktop file to ~/.local/share/applications/
# If you'd prefer to do this manually, instructions are in the README at https://codeberg.org/LinuxNation/svi/

set -e

echo "Installing Svi..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "This script will install system dependencies and the binary to system directories."
  echo "You must run this script with sudo or as root."
  echo "Usage: sudo $0"
  exit 1
fi

# Install required system dependencies
echo "Installing required system dependencies..."
sudo xbps-install -Sy parted python3-gobject

# Download the latest binary archive
echo "Downloading the latest svi binary archive..."
ARCHIVE_URL="https://codeberg.org/LinuxNation/svi/releases/download/v0.1.1/svi-0.1.1x86_64.tar.gz"
if command -v wget >/dev/null 2>&1; then
    wget -O svi-0.1.1x86_64.tar.gz "$ARCHIVE_URL"
else
    echo "Error: wget is not available to download the archive."
    exit 1
fi

# Check if the archive was downloaded successfully
if [ ! -f "svi-0.1.1x86_64.tar.gz" ]; then
    echo "Error: Failed to download the archive file!"
    exit 1
fi

# Extract the archive
tar -xzf svi-0.1.1x86_64.tar.gz

# Check if the svi folder exists and contains the binary
if [ ! -d "svi" ]; then
    echo "Error: Archive does not contain the expected 'svi' folder!"
    exit 1
fi

# Create the applications directory if it doesn't exist
mkdir -p ~/.local/share/applications/

# Copy the desktop file to the user's applications directory
echo "Installing desktop file to ~/.local/share/applications/..."
cp svi/svi.desktop ~/.local/share/applications/


# Copy the binary to /usr/local/bin/
echo "Installing binary to /usr/local/bin/..."
sudo cp svi/svi /usr/local/bin/
sudo chmod +x /usr/local/bin/svi

# Clean up extracted folder and archive
rm -rf svi svi-0.1.1x86_64.tar.gz

echo "Installation completed successfully!"
echo ""
echo "To run the installer, use:"
echo "  sudo svi"
echo ""
echo "You can also launch it from your desktop environment's applications menu."
