#!/bin/bash

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
source .bashrc

# imagen de fondo
# Ejecutar Dolphin.Root
# /usr/share/wallpapers/
# crear directorio Magna
# Copiar /Fonds/Magna-Logo-Wallpaper-With-Plasma-Logo.png /usr/share/wallpapers/Magna/

# imagen konsole
# Ejecutar Dolphin.Root
# /usr/share/wallpapers/
# crear directorio Bodhi
# Copiar /Fondos/Bodhi.png /usr/share/wallpapers/Bodhi/

# servicio cupsd localhost:631
sudo ln -s /etc/sv/cupsd /var/service
sudo usermod -aG lpadmin hooperman

#JDownloader
chmod +x JD2Setup_x64.sh
./JD2Setup_x64.sh

# Libre.Office.Tango.Theme
# Doble click al archivo Tango-iconset.oxt

# PhotoGIMP
# Darle doble clic al archivo PhotoGIMP-master.zip e ir a la carpeta:
# .var/app/org.gimp.GIMP/config/GIMP/2.10/
# Seleccionar las carpetas desde brushes hasta unitrc
# Arrastar estas carpetas a:
# /home/hooperman/.config/GIMP/2.10/
# Sobre escribir todos los archivos

# fmpegthumbs Abrir Dolphin, Configurar, Configurar Dolphin, Vistas Previas, marcar Archivos de Video (fmpegthumbs)

# Atajos de teclado
# Windows Key + L: Bloquear la Sesion. Ver archivo Atajo.01.Bloquear.png
# Windows Key + D: Dar Vistazo al Escritorio. Ver archivo Atajo.02.Escritorio.png
# Windows Key + Flechas: Situar las Ventanas. Ver archivo Atajo..03.Ventanas.png

# Configurar Spectacle. Ver archivo Spectacle.png

# Activar Bloque Numerico

# Ocultar Musica

# Ocultar Archivos Recientes

# reiniciar sistema
sudo reboot
