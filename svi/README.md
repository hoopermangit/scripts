# Svi
Simple Void Installer - A graphical installer for Void Linux, built with GTK4 and Python.

## State

The project is currently in alpha. It's still incomplete and undergoes frequent major changes.
If you'd still like to test the installer, I'd appreciate any feedback and bug reports.

## Installation

### With install script
1. Update xbps and install wget
```bash
sudo xbps-install -S xbps wget
```
2. Download and run the install script
```bash
wget -O install.sh https://codeberg.org/LinuxNation/svi/raw/branch/main/install.sh && sudo sh install.sh
```
3. Run the binary with root privileges
```bash
sudo svi
```

### Manually
1. Update xbps and install dependencies
```bash
sudo xbps-install -S xbps tar parted python3-gobject
```
2. Download the [latest](https://codeberg.org/LinuxNation/void-installer/releases) release
3. Extract the downloaded .tar archive
```bash
sudo tar -xf svi-versionx86_64.tar.gz
```
4. Open the svi folder
```bash
cd svi
```
5. Run the binary with root privileges
```bash
sudo ./svi
```

### Build from source
1. Clone the repository
```bash
  git clone https://codeberg.org/LinuxNation/void-installer.git
```
2. Open the svi folder
```bash
cd svi
```
3. Run the setup.sh script
```bash
./setup.sh
```
4. Compile the application
```bash
./compile.sh
```
5. Run the binary with root privileges
```bash
sudo ./svi
```
