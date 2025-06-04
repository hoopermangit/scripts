#!/bin/bash

# actualizar xbps
sudo xbps-install -u xbps

# actualizar repositorios
sudo xbps-install -Sy void-repo-debug void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
sudo xbps-install -Sy alsa-pipewire ark base-devel bpytop chromium cups curl epson-inkjet-printer-escpr exfatprogs fastfetch ffmpegthumbs filezilla galculator gimp gparted gsmartcontrol gwenview hblock hunspell-es iscan kde5 kde5-baseapps kdenlive kolourpaint krita kwrite libjack-pipewire libreoffice libreoffice-i18n-es mkvtoolnix-gui mpv nano NetworkManager okular pipewire pulseaudio qbittorrent rsync sddm smplayer spectacle topgrade unrar wget wine wine-32bit xtools-minimal xorg xournal

# instalar playonlinux
sudo xbps-install -Sy playonlinux

# instalar fonts
sudo cp -r JetBrainsMono.Font/ Menlo.Font/ Office.Fonts/ Windows.Fonts/ /usr/share/fonts/
sudo fc-cache -f -v

# imagenes terminal y escritorio
sudo cp -r Bodhi/ /usr/share/wallpapers/
sudo cp -r Magna/ /usr/share/wallpapers/

# añadir usuario a grupo cups localhost:631
sudo usermod -aG lpadmin hooperman

# iniciar servicios
sudo ln -s /etc/sv/cupsd /var/service
sudo ln -s /etc/sv/dbus /var/service
sudo ln -s /etc/sv/NetworkManager /var/service
sudo ln -s /etc/sv/sddm /var/service

# sudo reboot
