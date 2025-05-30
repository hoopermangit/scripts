#!/bin/bash

# void linux instalar lxde

# remover firefox
sudo xbps-remove -Ry firefox

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
sudo xbps-install -Sy 7zip 7zip-unrar barrier barrier bpytop chromium cups curl epson-inkjet-printer-escpr exfatprogs fastfetch filezilla flameshot galculator gparted gwenview hunspell-es iscan kolourpaint leafpad libreoffice libreoffice-i18n-es lxde mpv nano okular qbittorrent rsync smplayer wget

# instalar fonts
sudo cp -r Menlo.Font/ Windows.Fonts/ JetBrainsMono.Font/ /usr/share/fonts/
sudo fc-cache -f -v

# imagenes terminal y escritorio
sudo cp -r Bodhi/ Magna/ /usr/share/lxde/wallpapers/

# añadir usuario a grupo cups localhost:631
sudo usermod -aG lpadmin hooperman

# iniciar servicios
sudo ln -s /etc/sv/cupsd /var/service

# sudo reboot
