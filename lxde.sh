#!/bin/bash

# void linux install lxde from xfce

# remove firefox
sudo xbps-remove -Ry firefox

# update repositories
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# update system
sudo xbps-install -Suy

# install packages
sudo xbps-install -Sy 7zip 7zip-unrar barrier barrier bpytop chromium cups curl exfatprogs fastfetch filezilla flameshot galculator gparted gwenview hunspell-es kolourpaint leafpad libreoffice libreoffice-i18n-es lxde mpv nano okular qbittorrent rsync smplayer wget

# install fonts
sudo cp -r Menlo.Font/ Windows.Fonts/ JetBrainsMono.Font/ /usr/share/fonts/
sudo fc-cache -f -v

# images for terminal and desktop
sudo cp -r Bodhi/ Magna/ /usr/share/lxde/wallpapers/

# add user hooperman to cups localhost:631
sudo usermod -aG lpadmin hooperman

# start services
sudo ln -s /etc/sv/cupsd /var/service

# remove xfce
sudo xbps-remove -Ry xfce4* xfwm4

# move lxpolkit
sudo mv /etc/xdg/autostart/lxpolkit.desktop /home/hooperman/Descargas

# remove lxpolkit
sudo rm /home/hooperman/Descargas/lxpolkit.desktop

# install elogind
sudo xbps-install -Sy elogind

# remove orphaned files
sudo xbps-remove -Oov

# sudo reboot
sudo reboot
