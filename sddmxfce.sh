#!/bin/bash

# remover lightdm

sudo xbps-remove -R lightdm

# iniciar el servicio sddm

sudo ln -s /etc/sv/sddm /var/service
