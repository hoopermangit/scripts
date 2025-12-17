#!/bin/bash

# update system
topgrade

# update blockers
sudo hblock

# clean cache
sudo rm -rf /home/hooperman/.cache/thumbnails/large/
sudo rm -rf /home/hooperman/.cache/thumbnails/normal/
sudo rm -rf /home/hooperman/.cache/thumbnails/x-large/
sudo rm -rf /home/hooperman/.cache/thumbnails/xx-large/

# remove orphaned files
sudo xbps-remove -Oov
