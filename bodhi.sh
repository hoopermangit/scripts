#!/bin/bash

# bodhi linux actualizar repositorios
sudo apt-get update

# actualizar sistema
sudo apt-get dist-upgrade

# instalar paquetes
sudo apt-get install fastfetch hunspell-es libreoffice libreoffice-l10n-es lxde

# instalar fonts
sudo cp -r JetBrainsMono.Font/ Menlo.Font/ Office.Fonts/ Windows.Fonts/ /usr/share/fonts/
sudo fc-cache -f -v

# reboot
sudo reboot
