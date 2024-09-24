#!/bin/bash

# void linux instalar kde

# remover firefox
sudo xbps-remove -R firefox

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
sudo xbps-install -Sy ark barrier barrier-gui bpytop chromium cups curl epson-inkjet-printer-escpr fastfetch filezilla fmpegthumbs galculator gimp gparted gutenprint gwenview hunspell-es imagescan iscan kde5 kde5-baseapps kdenlive kolourpaint krita kwrite libreoffice libreoffice-i18n-es mkvtoolnix-gui mpv nano okular qbittorrent rsync spectacle smplayer wget wine wine-32bit xournal

# instalar playonlinux
sudo xbps-install -Sy playonlinux

# instalar fonts
sudo cp -r JetBrainsMono.Font/ Menlo.Font/ Office.Fonts/ Windows.Fonts/ /usr/share/fonts/
sudo fc-cache -f -v

# reiniciar sistema seleccionar plasma X11
sudo reboot
