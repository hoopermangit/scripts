#!/bin/bash

# instalar paquetes
sudo xbps-install -Sy alsa-pipewire base-devel kde5 kde5-baseapps libjack-pipewire NetworkManager pipewire pulseaudio sddm xorg

# activar servicios
sudo ln -s /etc/sv/dbus /var/service
sudo ln -s /etc/sv/NetworkManager /var/service
sudo ln -s /etc/sv/sddm /var/service
