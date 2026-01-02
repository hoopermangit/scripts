# Svi
Simple Void Installer - Ein grafischer Installer für Void Linux, erstellt mit GTK4 und Python.

## Status

Das Projekt befindet sich derzeit in der Alpha-Phase. Es ist noch unvollständig und unterliegt häufigen größeren Änderungen.
Wenn du dennoch den Installer testen möchtest, freue ich mich über Feedback und Fehlerberichte.

## Installation

### Mit Installations-Skript
1. Aktualisiere xbps und installiere wget
```bash
sudo xbps-install -S xbps wget
```
2. Lade das Installations-Skript herunter und führe es aus
```bash
wget -O install.sh https://codeberg.org/LinuxNation/svi/raw/branch/main/install.sh && sudo sh install.sh
```
3. Führe die Anwendung mit Root-Rechten aus
```bash
sudo svi
```

### Manuell
1. Aktualisiere xbps und installiere die Abhängigkeiten
```bash
sudo xbps-install -S xbps tar parted python3-gobject
```
2. Lade die [neueste](https://codeberg.org/LinuxNation/void-installer/releases) Version herunter
3. Entpacke das heruntergeladene .tar-Archiv
```bash
sudo tar -xf svi-versionx86_64.tar.gz
```
4. Öffne den svi-Ordner
```bash
cd svi
```
5. Führe die Anwendung mit Root-Rechten aus
```bash
sudo ./svi
```

### Build from source
1. Repository klonen
```bash
  git clone https://codeberg.org/LinuxNation/void-installer.git
```
2. Öffne den svi-Ordner
```bash
cd svi
```
3. Führe das setup.sh-Skript aus
```bash
./setup.sh
```
4. Kompiliere die Anwendung
```bash
./compile.sh
```
5. Führe die Anwendung mit Root-Rechten aus
```bash
sudo ./svi
```
