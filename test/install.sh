#!/bin/bash
# -------------------------------------------------------------
# Void Linux – Dependencias para el instalador gráfico
# -------------------------------------------------------------
# Installiert alle benötigten Pakete für:
# - GTK4 / Adwaita Python Installer
# - Partitioning (parted, mkfs, btrfs, xfs, swap)
# - rsync Live-System Copy
# - GRUB Installation (UEFI + BIOS)
# - Optional: Flatpak, Printer, NVIDIA
# -------------------------------------------------------------

set -e

echo ">>> Void Installer – Instalar dependencias..."

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

# --- Partitioning, System-Tools ---
xbps-install -Sy \
    parted \
    e2fsprogs \
    dosfstools \
    btrfs-progs \
    xfsprogs \
    lvm2

# --- Bootloader (UEFI + BIOS) --- grub-i386-pc is obsolete
xbps-install -Sy \
    grub-x86_64-efi \
    efibootmgr

# --- Optional Components (comentar con # si no es necesario.) ---

# Flatpak Support
xbps-install -Sy \
    flatpak \
    xdg-desktop-portal \
    xdg-desktop-portal-gtk

# Printer Support (CUPS + Filter + HP)
xbps-install -Sy \
    cups \
    cups-filters \

echo
echo ">>> ¡Listo! Se han instalado todas las dependencias."
echo ">>> Ahora puedes iniciar el instalador."
