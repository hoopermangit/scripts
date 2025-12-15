#!/bin/bash
# -------------------------------------------------------------
# Void Linux – Dependencies for the graphical installer
# -------------------------------------------------------------
# Installs all required packages for:
# - GTK4 / Adwaita Python Installer
# - Partitioning (parted, mkfs, btrfs, xfs, swap)
# - rsync Live-System Copy
# - GRUB Installation (UEFI + BIOS)
# - Optional: Flatpak, Printer, NVIDIA
# -------------------------------------------------------------

set -e

echo ">>> Installing Dependencies..."

# --- Basis: System + Python + GTK4 GUI ---
xbps-install -Sy \
    python3 \
    python3-gobject \
    gtk4 \
    libadwaita \
    bash \
    shadow \
    util-linux \
    xbps \
    rsync \
    tar

# --- Partitioning, File System -Tools ---
xbps-install -Sy \
    parted \
    # e2fsprogs \
    # dosfstools \
    # btrfs-progs \
    # xfsprogs \
    # lvm2

# --- Bootloader (UEFI + BIOS) ---
xbps-install -Sy \
    # grub-x86_64-efi \
    # grub-i386-pc \
    efibootmgr

# --- Optional Components (you can comment them out if they are not needed) ---

# Flatpak Support
xbps-install -Sy \
    flatpak \
    xdg-desktop-portal \
    xdg-desktop-portal-gtk

# Printer Support (CUPS + Filter + HP)
xbps-install -Sy \
    cups \
    cups-filters \
    hplip

# NVIDIA Drivers (Non-Free)
# xbps-install -Sy \
#   nvidia \
#   nvidia-libs \
#   nvidia-dkms

echo
echo ">>> Done! All dependencies have been installed."
echo ">>> You can now start the installer."
