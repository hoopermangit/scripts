#!/bin/bash

# remover firefox

sudo xbps-remove -R firefox

# actualizar repositorios

sudo xbps-install -Sy void-repo-nonfree void-repo-multilib void-repo-multilib-nonfree void-repo-debug

# actualizar sistema

sudo xbps-install -Suy

# instalar paquetes

sudo xbps-install -Sy ark bpytop chromium epson-inkjet-printer-escpr filezilla galculator gimp gutenprint hunspell-es imagescan iscan kde5 kde5-baseapps kolourpaint krita kwrite libreoffice libreoffice-i18n-es mkvtoolnix-gui nano neofetch okular qbittorrent spectacle smplayer xournal

# instalar fonts

sudo cp -r JetBrainsMono.Font/ Menlo.Font/ Office.Fonts/ Windows.Fonts/ /usr/share/fonts/

sudo fc-cache -f -v

# reiniciar sistema
