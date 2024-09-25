#!/bin/bash

# void linux instalar kde

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes

sudo xbps-install -Sy alsa-pipewire ark barrier barrier-gui base-system bpytop brltty chromium chrony cryptsetup cups curl dejavu-fonts-ttf dialog epson-inkjet-printer-escpr espeakup fastfetch ffmpegthumbs filezilla font-misc-misc galculator gimp git gnome-keyring gnome-themes-standard gparted grub-i386-efi grub-x86_64-efi gutenprint gvfs-afc gvfs-mtp gvfs-smb gwenview hunspell-es  imagescan iscan kde5 kde5-baseapps kdenlive kolourpaint krita kwrite libreoffice libreoffice-i18n-es lvm2 mdadm mkvtoolnix-gui mpv nano network-manager-applet okular orca pipewire playonlinux qbittorrent rsync setxkbmap smplayer spectacle terminus-font udisks2 void-docs-browse void-live-audio wget wine wine-32bit xauth xmirror xorg-input-drivers xorg-minimal xorg-video-drivers xournal xtools-minimal

# instalar playonlinux
sudo xbps-install -Sy playonlinux

# instalar fonts
sudo cp -r JetBrainsMono.Font/ Menlo.Font/ Office.Fonts/ Windows.Fonts/ /usr/share/fonts/
sudo fc-cache -f -v

# oh my bash
bash -c "$(wget https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh -O -)"

# imagen konsole e imagen de escritorio
sudo cp -r Bodhi/ Magna/ /usr/share/wallpapers/

# añadir hooperman a grupo cups
sudo usermod -aG lpadmin hooperman

# iniciar servicios
sudo ln -s /etc/sv/dbus /var/service
sudo ln -s /etc/sv/NetworkManager /var/service
sudo ln -s /etc/sv/cupsd /var/service
sudo ln -s /etc/sv/sddm /var/service
