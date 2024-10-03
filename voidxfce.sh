#!/bin/bash

# remover firefox
sudo xbps-remove -R firefox
sudo xbps-remove -Oov

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
sudo xbps-install -Sy 7zip 7zip-unrar bpytop chromium epdfview epson-inkjet-printer-escpr fastfetch flameshot galculator gpicview gutenprint hunspell-es imagescan iscan krita leafpad libreoffice libreoffice-i18n-es lxde mpv nano smplayer

# instalar fonts
sudo cp -r Menlo.Font/ Windows.Fonts/ JetBrainsMono.Font/ /usr/share/fonts/
sudo fc-cache -f -v

# reiniciar sistema
sudo reboot
