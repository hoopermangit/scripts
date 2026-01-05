#!/bin/bash
# -------------------------------------------------------------
# Void Linux – Abhängigkeiten für den grafischen Installer
# -------------------------------------------------------------
# Installiert alle benötigten Pakete für:
# - GTK4 / Adwaita Python Installer
# - Partitionierung (parted, mkfs, btrfs, xfs, swap)
# - rsync Live-System Copy
# - GRUB Installation (UEFI + BIOS)
# - Optional: Flatpak, Drucker, NVIDIA
# -------------------------------------------------------------

set -e

echo ">>> Void Installer – Installiere Abhängigkeiten..."

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

# --- Partitionierung, Dateisystem-Tools ---
xbps-install -Sy \
    parted \
    e2fsprogs \
    dosfstools \
    btrfs-progs \
    xfsprogs \
    lvm2

# --- Bootloader (UEFI + BIOS) ---
xbps-install -Sy \
    grub-x86_64-efi \
    grub-i386-pc \
    efibootmgr

# --- Optionale Komponenten (kannst du auskommentieren, falls nicht benötigt) ---

# Flatpak Support
xbps-install -Sy \
    flatpak \
    xdg-desktop-portal \
    xdg-desktop-portal-gtk

# Drucker Support (CUPS + Filter + HP)
xbps-install -Sy \
    cups \
    cups-filters \
    hplip

echo
echo ">>> Fertig! Alle Abhängigkeiten wurden installiert."
echo ">>> Du kannst jetzt den Installer starten."
