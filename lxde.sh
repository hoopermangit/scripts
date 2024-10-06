#!/bin/bash

# void linux instalar lxde

# remover firefox
sudo xbps-remove -Ry firefox
sudo xbps-remove -Oov

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
7zip 7zip-unrar alsa-pipewire barrier barrier base-system bpytop brltty chromium chrony cryptsetup cups curl dejavu-fonts-ttf dialog elogind epdfview epson-inkjet-printer-escpr espeakup fastfetch filezilla flameshot font-misc-misc galculator git gnome-keyring gnome-themes-standard gparted gpicview grub-i386-efi grub-x86_64-efi gutenprint gvfs-afc gvfs-mtp gvfs-smb hunspell-es imagescan iscan kolourpaint leafpad libreoffice libreoffice-i18n-es lightdm lightdm-gtk3-greeter lvm2 lxde mdadm mpv nano network-manager-applet orca pipewire qbittorrent rsync setxkbmap smplayer terminus-font udisks2 void-docs-browse void-live-audio wget xauth xmirror xorg-input-drivers xorg-minimal xorg-video-drivers xtools-minimal

# instalar fonts
sudo cp -r Menlo.Font/ Windows.Fonts/ JetBrainsMono.Font/ /usr/share/fonts/
sudo fc-cache -f -v

# imagenes terminal y escritorio
sudo cp -r Bodhi/ Magna/ /usr/share/lxde/wallpapers/

# añadir usuario a grupo cups localhost:631
sudo usermod -aG lpadmin hooperman

# iniciar servicios
sudo ln -s /etc/sv/dbus /var/service
sudo ln -s /etc/sv/NetworkManager /var/service
sudo ln -s /etc/sv/lightdm /var/service
sudo ln -s /etc/sv/cupsd /var/service

# reiniciar sistema
sudo reboot
