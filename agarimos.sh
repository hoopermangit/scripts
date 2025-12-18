#!/bin/bash

# void linux install kde from agarimos

# remove firefox
sudo xbps-remove -Ry firefox

# update repositories
sudo xbps-install -Sy void-repo-debug void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree

# update system
sudo xbps-install -Suy

# install packages
sudo xbps-install -Sy ark bpytop chromium cups exfatprogs filezilla flatpak galculator gimp gparted gsmartcontrol gutenprint gwenview hunspell-es kde5 kde5-baseapps kdenlive kolourpaint krita kwrite libreoffice libreoffice-i18n-es mkvtoolnix-gui mpv okular qbittorrent smplayer unrar xournal

# install Jdownloader
flatpak install --from JDownloader.flatpakref

# install fonts
sudo cp -r JetBrainsMono.Font/ Menlo.Font/ Office.Fonts/ Windows.Fonts/ /usr/share/fonts/
sudo fc-cache -f -v

# images for terminal and desktop
sudo cp -r Bodhi/ /usr/share/wallpapers/
sudo cp -r Magna/ /usr/share/wallpapers/

# add user hooperman to cups localhost:631
sudo usermod -aG lpadmin hooperman

# remove orphaned files
sudo xbps-remove -Oov

# sudo reboot
sudo reboot
