#!/bin/bash

# void linux instalar kde

# remover firefox
sudo xbps-remove -Ry firefox

# actualizar repositorios
sudo xbps-install -Sy void-repo-debug void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
sudo xbps-install -Sy ark bpytop chromium cups curl epson-inkjet-printer-escpr exfatprogs fastfetch ffmpegthumbs filezilla galculator gimp gparted gssmartcontrol gutenprint gwenview hblock hunspell-es iscan kde5 kde5-baseapps kdenlive kolourpaint krita kwrite libreoffice libreoffice-i18n-es mkvtoolnix-gui mpv nano okular qbittorrent rsync smplayer spectacle topgrade unrar wget wine wine-32bit xtools-minimal xournal

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
sudo ln -s /etc/sv/sddm /var/service

# sudo reboot
