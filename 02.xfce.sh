#!/bin/bash

# void linux remover xfce

# remover lifgthdm
sudo xbps-remove -Ry lightdm

# remover xfce
sudo xbps-remove -Ry xfce4* xfwm4
sudo xbps-remove -Ry libxfce4ui-4.18.6_1 xfce4-pulseaudio-plugin-0.4.8_1
sudo xbps-remove -Oov

# iniciar el servicio sddm seleccionar plasma X11
sudo ln -s /etc/sv/sddm /var/service
