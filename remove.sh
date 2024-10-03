#!/bin/bash

# remover firefox
sudo xbps-remove -R firefox
sudo xbps-remove -Oov

# void linux remover xfce

# remover xfce
sudo xbps-remove -Ry xfce4* xfwm4
sudo xbps-remove -Ry libxfce4ui-4.18.6_1 xfce4-pulseaudio-plugin-0.4.8_1
sudo xbps-remove -Oov
sudo xbps-install -Sy elogind

# reiniciar sistema
# seleccionar lxde
sudo reboot
