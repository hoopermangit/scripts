#!/bin/bash

# remover xfce

sudo xbps-remove -R xfce4* xfwm4

sudo xbps-remove -R libxfce4ui-4.18.6_1 xfce-pulseaudio-plugin-0.4.8_1

sudo xbps-remove -Oov
