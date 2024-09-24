#!/bin/bash

# void linux personalizar kde

# oh my bash Line 12 replace "font" with "powerline"
bash -c "$(wget https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh -O -)"

# imagen konsole e imagen de escritorio
sudo cp -r Bodhi/ Magna/ /usr/share/wallpapers/

# servicio cupsd localhost:631
sudo ln -s /etc/sv/cupsd /var/service
sudo usermod -aG lpadmin hooperman
