#!/bin/bash

# remover firefox
sudo xbps-remove -R firefox

# actualizar repositorios
sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema
sudo xbps-install -Suy

# instalar paquetes
sudo xbps-install -Sy ark barrier barrier-gui bpytop chromium curl epson-inkjet-printer-escpr fastfetch filezilla galculator gimp gparted gutenprint hunspell-es imagescan iscan kde5 kde5-baseapps kdenlive kolourpaint krita kwrite libreoffice libreoffice-i18n-es mkvtoolnix-gui nano okular qbittorrent spectacle smplayer wget wine wine-32bit xournal

# instalar fonts
sudo cp -r JetBrainsMono.Font/ Menlo.Font/ Office.Fonts/ Windows.Fonts/ /usr/share/fonts/
sudo fc-cache -f -v

# reiniciar sistema Seleccionar Plasma X11
sudo reboot

# remover lightdm
sudo xbps-remove -R lightdm

# remover xfce

sudo xbps-remove -R xfce4* xfwm4

sudo xbps-remove -R libxfce4ui-4.18.6_1 xfce4-pulseaudio-plugin-0.4.8_1

sudo xbps-remove -Oov

# iniciar el servicio sddm
sudo ln -s /etc/sv/sddm /var/service

# oh my bash Line 12 replace "font" with "powerline"
bash -c "$(wget https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh -O -)"
sudo nano -l -m /home/hooperman/.bashrc

# reiniciar sistema
sudo reboot
