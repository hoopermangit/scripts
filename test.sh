#!/bin/bash

# void linux instalar kde

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes

sudo xbps-install alsa-pipewire ark barrier barrier-gui base-system bpytop brltty chromium chrony cryptsetup cups curl dejavu-fonts-ttf dialog epson-inkjet-printer-escpr espeakup fastfetch ffmpegthumbs filezilla font-misc-misc galculator gimp git gnome-keyring gnome-themes-standard gparted grub-i386-efi grub-x86_64-efi gutenprint gvfs-afc gvfs-mtp gvfs-smb gwenview hunspell-es  imagescan iscan kde5 kde5-baseapps kdenlive kolourpaint krita kwrite libreoffice libreoffice-i18n-es lightdm-gtk3-greeter lvm2 mdadm mkvtoolnix-gui mpv nano network-manager-applet okular orca pipewire playonlinux qbittorrent rsync setxkbmap smplayer spectacle terminus-font udisks2 void-docs-browse void-live-audio wget wine wine-32bit xauth xmirror xorg-input-drivers xorg-minimal xorg-video-drivers xournal xtools-minimalgit
