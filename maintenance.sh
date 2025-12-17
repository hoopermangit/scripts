#!/bin/bash

# update system
topgrade

# update blockers
sudo hblock

# clean cache and remove orphan files
sudo rm -rf /home/hooperman/.cache/thumbnails/large/
sudo rm -rf /home/hooperman/.cache/thumbnails/normal/
sudo rm -rf /home/hooperman/.cache/thumbnails/x-large/
sudo rm -rf /home/hooperman/.cache/thumbnails/xx-large/
sudo xbps-remove -Oov
