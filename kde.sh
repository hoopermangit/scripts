#!/bin/bash

# void linux instalar kde

# remover firefox
sudo xbps-remove -Ry firefox

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
sudo xbps-install -Sy ark barrier barrier-gui bpytop chromium cups curl exfatprogs fastfetch ffmpegthumbs filezilla galculator gimp gparted gssmartcontrol gutenprint gwenview hunspell-es imagescan iscan kde5 kde5-baseapps kdenlive kolourpaint krita kwrite libreoffice libreoffice-i18n-es mkvtoolnix-gui mpv nano okular qbittorrent rsync smplayer spectacle unrar wget wine wine-32bit xournal

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
