#!/bin/bash

# copiar fonts

sudo cp -r JetBrainsMono.Font/ Menlo.Font/ Office.Fonts/ Windows.Fonts/ /usr/share/fonts

# actualizar cache de fonts

sudo fc-cache -f -v
