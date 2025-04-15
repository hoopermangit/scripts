#!/bin/bash

# void linux instalar kde

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
sudo xbps-install -Sy ark barrier barrier-gui base-devel bpytop chromium cups curl epson-inkjet-printer-escpr fastfetch ffmpegthumbs filezilla galculator gimp gparted gwenview hunspell-es iscan kde5 kde5-baseapps kdenlive kolourpaint krita kwrite libreoffice libreoffice-i18n-es mkvtoolnix-gui mpv nano NetworkManager octoxbps okular pulseaudio qbittorrent rsync sddm smplayer spectacle unrar wget wine wine-32bit xorg xournal

# instalar playonlinux
sudo xbps-install -Sy playonlinux

# instalar fonts
sudo cp -r JetBrainsMono.Font/ Menlo.Font/ Office.Fonts/ Windows.Fonts/ /usr/share/fonts/
sudo fc-cache -f -v

# imagenes terminal y escritorio
sudo cp -r Bodhi/ Magna/ /usr/share/wallpapers/

# añadir usuario a grupo cups localhost:631
sudo usermod -aG lpadmin hooperman

# iniciar servicios
sudo ln -s /etc/sv/cupsd /var/service
sudo ln -s /etc/sv/sddm /var/service

# sudo reboot
