#!/bin/bash
# -------------------------------------------------------------
# Void Linux – Dependencias para el instalador gráfico
# -------------------------------------------------------------
# Instala todos los paquetes necesarios para:
# - GTK4 / Adwaita / Python
# - Particionado (parted, mkfs, btrfs, xfs, swap)
# - rsync
# - GRUB Installation (UEFI + BIOS)
# - Opcional: Flatpak, Printer, NVIDIA
# -------------------------------------------------------------

set -e

echo "Instalar dependencias"

# --- Sistema + Python + GTK4 GUI ---
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

# --- Particionado, Herramientas del sistema de archivos ---
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
    efibootmgr

# --- Componentes opcionales (puedes comentarlos si no son necesarios) ---

# Flatpak
xbps-install -Sy \
    flatpak \
    xdg-desktop-portal \
    xdg-desktop-portal-gtk

# Printer (CUPS + Filter + HP)
#   hplip
xbps-install -Sy \
    cups \
    cups-filters \

# NVIDIA Treiber (Non-Free)
# xbps-install -Sy \
#   nvidia \
#   nvidia-libs \
#   nvidia-dkms

echo
echo "¡Listo! Se han instalado todas las dependencias."
echo "Ahora puedes iniciar el instalador."
