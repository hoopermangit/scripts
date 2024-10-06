#!/bin/bash

# void linux instalar lxde

# remover firefox
sudo xbps-remove -Ry firefox
sudo xbps-remove -Oov

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
sudo xbps-install -Sy 7zip 7zip-unrar barrier barrier bpytop chromium cups curl elogind epdfview epson-inkjet-printer-escpr fastfetch filezilla flameshot galculator gparted gpicview gutenprint hunspell-es imagescan iscan kolourpaint leafpad libreoffice libreoffice-i18n-es lxde mpv nano qbittorrent rsync smplayer wget

# instalar fonts
sudo cp -r Menlo.Font/ Windows.Fonts/ JetBrainsMono.Font/ /usr/share/fonts/
sudo fc-cache -f -v

# imagenes terminal y escritorio
sudo cp -r Bodhi/ Magna/ /usr/share/lxde/wallpapers/

# añadir usuario a grupo cups localhost:631
sudo usermod -aG lpadmin hooperman

# iniciar servicios
sudo ln -s /etc/sv/dbus /var/service
sudo ln -s /etc/sv/NetworkManager /var/service
sudo ln -s /etc/sv/lightdm /var/service
sudo ln -s /etc/sv/cupsd /var/service

# reiniciar sistema
sudo reboot
