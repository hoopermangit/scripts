#!/bin/bash

# remover xfce

sudo xbps-remove -R xfce4* xfconf xfdesktop4 xfwm4 exo-utils thunar

sudo xbps-remove -Oov

sudo xbps-install -Sy elogind
