#!/bin/bash

# void linux remover xfce

# remover xfce
sudo xbps-remove -Ry xfce4* xfwm4

# remover archivos huerfanos
sudo xbps-remove -Oov

# sudo reboot
