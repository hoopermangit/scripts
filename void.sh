#!/bin/bash

# actualizar paquete xbps
sudo xbps-install -u xbps

# remover firefox
sudo xbps-remove -Ry firefox

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes (epson-inkjet-printer-escpr imagescan iscan playonlinux spectacle wine wine-32bit)
sudo xbps-install -Sy ark barrier barrier-gui bpytop chromium cups curl exfatprogs fastfetch ffmpegthumbs filezilla flatpak galculator gimp gparted gssmartcontrol gwenview hunspell-es kde5 kde5-baseapps kdenlive kolourpaint krita kwrite libreoffice libreoffice-i18n-es mkvtoolnix-gui mpv nano okular qbittorrent rsync smplayer unrar wget xournal

# instalar Jdownloader
sudo flatpak install --from JDownloader.flatpakref

# instalar fonts
sudo cp -r JetBrainsMono.Font/ Menlo.Font/ Office.Fonts/ Windows.Fonts/ /usr/share/fonts/
sudo fc-cache -f -v

# imagenes terminal y escritorio
sudo cp -r Bodhi/ Magna/ /usr/share/wallpapers/

# añadir usuario a grupo cups localhost:631
sudo usermod -aG lpadmin hooperman

# remover xfce
sudo xbps-remove -Ry xfce4* xfwm4
sudo xbps-remove -Ry libxfce4ui-4.18.6_1 xfce4-pulseaudio-plugin-0.4.8_1

# remover archivos huerfanos
sudo xbps-remove -Oov

# iniciar servicios
sudo ln -s /etc/sv/cupsd /var/service
sudo ln -s /etc/sv/sddm /var/service

# void linux instalar kde

# sudo reboot
