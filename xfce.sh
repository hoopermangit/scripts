#!/bin/bash

# void linux instalar xfce

# remover firefox
sudo xbps-remove -Ry firefox

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
sudo xbps-install -Sy 7zip 7zip-unrar barrier barrier bpytop chromium cups curl epdfview epson-inkjet-printer-escpr fastfetch filezilla flameshot galculator gparted gutenprint hunspell-es imagescan iscan kolourpaint libreoffice libreoffice-i18n-es mpv nano qbittorrent rsync smplayer wget

# instalar fonts
sudo cp -r Menlo.Font/ Windows.Fonts/ JetBrainsMono.Font/ /usr/share/fonts/
sudo fc-cache -f -v

# imagenes terminal y escritorio
sudo cp -r Bodhi/ Magna/ /usr/share/backgrounds/xfce/

# añadir usuario a grupo cups localhost:631
sudo usermod -aG lpadmin hooperman

# iniciar servicios
sudo ln -s /etc/sv/cupsd /var/service

# sudo reboot
