#!/bin/bash

# actualizar sistema
sudo topgrade

# actualizar bloqueadores
sudo hblock

# limpiar cache y borrar archivos huerfanos
sudo xbps-remove -Oov
