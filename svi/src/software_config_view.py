import gi

gi.require_version("Gtk", "4.0")
import subprocess
from typing import List

from gi.repository import Gtk

MIRRORS = [
    "Standard - https://repo-default.voidlinux.org/",
    "Weltweit (Tier 1) - https://repo-fastly.voidlinux.org/",
    "Frankfurt (Tier 1) - https://repo-de.voidlinux.org/",
    "Helsinki (Tier 1) - https://repo-fi.voidlinux.org/",
    "Chicago (Tier 1) - https://mirrors.servercentral.com/voidlinux/",
]

SERVICES_SET = [
    "chrony",
    "dbus",
    "lightdm",
    "NetworkManager",
    "polkit",
]

BASE_SET = [
    "espeakup",
    "void-live-audio",
    "brltty",
    "dialog",
    "cryptsetup",
    "lvm2",
    "mdadm",
    "void-docs-browse",
    "xtools-minimal",
    "xmirror",
    "chrony",
    "tmux",
    "grub-i386-efi",
    "grub-x86_64-efi",
]

XORG_SET = [
    "xorg-video-drivers",
    "xf86-video-intel",
    "font-misc-misc",
    "terminus-font",
    "dejavu-fonts-ttf",
    "xorg-minimal",
    "xorg-input-drivers",
    "setxkbmap",
    "xauth",
    "orca",
]

CINNAMON_SET = [
    "lightdm",
    "lightdm-gtk-greeter",
    "cinnamon",
    "gnome-keyring",
    "colord",
    "gnome-terminal",
    "gvfs-afc",
    "gvfs-mtp",
    "gvfs-smb",
    "udisks2",
]

XFCE_SET = [
    "lightdm",
    "lightdm-gtk-greeter",
    "xfce4",
    "gnome-themes-standard",
    "gnome-keyring",
    "network-manager-applet",
    "gvfs-afc",
    "gvfs-mtp",
    "gvfs-smb",
    "udisks2",
    "xfce4-pulseaudio-plugin",
]

BUNDLE_NVIDIA = ["nvidia", "nvidia-dkms", "nvidia-firmware"]
BUNDLE_PRINTER = ["cups", "cups-pdf", "cups-filters", "gutenprint"]
BUNDLE_PIPEWIRE = ["pipewire", "wireplumber", "alsa-pipewire"]
BUNDLE_NONFREE_CODECS = ["x264", "x265", "gst-plugins-bad1", "gst-plugins-ugly1"]
BUNDLE_FLATPAK = ["flatpak", "xdg-desktop-portal", "xdg-desktop-portal-gtk"]
BUNDLE_FIREFOX_DE = ["firefox", "firefox-i18n-de"]
BUNDLE_VIVALDI = ["vivaldi"]
BUNDLE_EVOLUTION = ["evolution"]
BUNDLE_THUNDERBIRD_DE = ["thunderbird", "thunderbird-i18n-de"]
BUNDLE_LIBREOFFICE_DE = ["libreoffice", "libreoffice-i18n-de"]
PKG_GNOME_CALENDAR = "gnome-calendar"
PKG_PAPERS = "papers"
PKG_EVINCE = "evince"
PKG_VLC = "vlc"
PKG_RHYTHMBOX = "rhythmbox"
PKG_KDENLIVE = "kdenlive"
PKG_OBS = "obs"


class SoftwareConfigView(Gtk.Box):
    # Page to select preferred applications and customizations
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for s in (
            self.set_margin_top,
            self.set_margin_bottom,
            self.set_margin_start,
            self.set_margin_end,
        ):
            s(6)

        title = Gtk.Label.new("Software & Konfiguration")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        self.append(title)
        sc = Gtk.ScrolledWindow()
        sc.set_vexpand(True)
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.append(sc)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sc.set_child(root)

        f_repo = Gtk.Frame(label="Repository Server")
        f_repo.add_css_class("card")
        root.append(f_repo)
        box_repo = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )
        f_repo.set_child(box_repo)
        mirror_label = Gtk.Label.new("Mirror:")
        box_repo.append(mirror_label)
        self.cmb_mirror = Gtk.ComboBoxText()
        for m in MIRRORS:
            self.cmb_mirror.append_text(m)
        try:
            idx = MIRRORS.index("Frankfurt (Tier 1) - https://repo-de.voidlinux.org/")
        except ValueError:
            idx = 0
        self.cmb_mirror.set_active(idx)
        box_repo.append(self.cmb_mirror)

        # ISO packages option
        f_iso = Gtk.Frame(label="Live-System Pakete")
        f_iso.add_css_class("card")
        root.append(f_iso)
        box_iso = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )
        f_iso.set_child(box_iso)
        self.cb_iso_packages = Gtk.CheckButton.new_with_label(
            "Alle Pakete vom Live-System übernehmen"
        )
        self.cb_iso_packages.set_active(True)
        self.cb_iso_packages.set_tooltip_text(
            "Installiert alle Pakete, die im Live-System derzeit vorhanden sind. "
            "Dadurch wird der installierte Zustand des Live-Systems auf die Festplatte kopiert."
        )
        box_iso.append(self.cb_iso_packages)

        f_de = Gtk.Frame(label="Desktop")
        f_de.add_css_class("card")
        root.append(f_de)
        box_de = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )
        f_de.set_child(box_de)
        self.cb_cinnamon = Gtk.CheckButton.new_with_label("Cinnamon Desktop")
        self.cb_cinnamon.set_active(False)
        box_de.append(self.cb_cinnamon)

        self.cb_xfce = Gtk.CheckButton.new_with_label("XFCE Desktop")
        self.cb_xfce.set_active(False)
        box_de.append(self.cb_xfce)

        f_extra = Gtk.Frame(label="Zusätzliche Pakete")
        f_extra.add_css_class("card")
        root.append(f_extra)
        grid_main = Gtk.Grid(
            column_spacing=20,
            row_spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )
        f_extra.set_child(grid_main)

        frame_system = Gtk.Frame(label="System")
        frame_system.add_css_class("card")
        grid_main.attach(frame_system, 0, 0, 1, 1)
        box_system = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=5,
            margin_bottom=5,
            margin_start=5,
            margin_end=5,
        )
        frame_system.set_child(box_system)
        self.cb_nvidia = Gtk.CheckButton.new_with_label("NVIDIA Treiber")
        box_system.append(self.cb_nvidia)
        self.cb_printer = Gtk.CheckButton.new_with_label("Druckerunterstützung")
        box_system.append(self.cb_printer)
        self.cb_pipewire = Gtk.CheckButton.new_with_label("PipeWire Audio-Stack")
        self.cb_pipewire.set_active(False)
        box_system.append(self.cb_pipewire)
        self.cb_codecs = Gtk.CheckButton.new_with_label("Nonfree Codecs")
        self.cb_codecs.set_active(False)
        box_system.append(self.cb_codecs)
        self.cb_flatpak = Gtk.CheckButton.new_with_label("Flatpak-Unterstützung")
        self.cb_flatpak.set_active(False)
        box_system.append(self.cb_flatpak)

        frame_internet = Gtk.Frame(label="Internet")
        frame_internet.add_css_class("card")
        grid_main.attach(frame_internet, 1, 0, 1, 1)
        box_internet = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=5,
            margin_bottom=5,
            margin_start=5,
            margin_end=5,
        )
        frame_internet.set_child(box_internet)
        self.cb_firefox = Gtk.CheckButton.new_with_label("Firefox (de)")
        self.cb_firefox.set_active(False)
        box_internet.append(self.cb_firefox)
        self.cb_vivaldi = Gtk.CheckButton.new_with_label("Vivaldi")
        box_internet.append(self.cb_vivaldi)
        self.cb_evolution = Gtk.CheckButton.new_with_label("Evolution")
        box_internet.append(self.cb_evolution)
        self.cb_thunderbird = Gtk.CheckButton.new_with_label("Thunderbird (de)")
        box_internet.append(self.cb_thunderbird)

        frame_office = Gtk.Frame(label="Office")
        frame_office.add_css_class("card")
        grid_main.attach(frame_office, 2, 0, 1, 1)
        box_office = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=5,
            margin_bottom=5,
            margin_start=5,
            margin_end=5,
        )
        frame_office.set_child(box_office)
        self.cb_libre = Gtk.CheckButton.new_with_label("LibreOffice (de)")
        box_office.append(self.cb_libre)
        self.cb_calendar = Gtk.CheckButton.new_with_label("GNOME Calendar")
        box_office.append(self.cb_calendar)
        self.cb_papers = Gtk.CheckButton.new_with_label("Papers")
        box_office.append(self.cb_papers)
        self.cb_evince = Gtk.CheckButton.new_with_label("Evince (PDF)")
        box_office.append(self.cb_evince)

        frame_media = Gtk.Frame(label="Multimedia")
        frame_media.add_css_class("card")
        grid_main.attach(frame_media, 3, 0, 1, 1)
        box_media = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=5,
            margin_bottom=5,
            margin_start=5,
            margin_end=5,
        )
        frame_media.set_child(box_media)
        self.cb_vlc = Gtk.CheckButton.new_with_label("VLC")
        box_media.append(self.cb_vlc)
        self.cb_rhythmbox = Gtk.CheckButton.new_with_label("Rhythmbox")
        box_media.append(self.cb_rhythmbox)
        self.cb_kdenlive = Gtk.CheckButton.new_with_label("Kdenlive")
        box_media.append(self.cb_kdenlive)
        self.cb_obs = Gtk.CheckButton.new_with_label("OBS Studio")
        box_media.append(self.cb_obs)

        f_copy = Gtk.Frame(label="Anpassungen kopieren")
        f_copy.add_css_class("card")
        root.append(f_copy)
        box_copy = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )
        f_copy.set_child(box_copy)

        # Radio buttons for copy options
        self.rb_copy_none = Gtk.CheckButton.new_with_label("Nichts kopieren")
        self.rb_copy_iso = Gtk.CheckButton.new_with_label("ISO-Anpassungen kopieren")
        self.rb_copy_include = Gtk.CheckButton.new_with_label(
            "Eigenen Include-Root Ortner kopieren"
        )

        self.rb_copy_iso.set_group(self.rb_copy_none)
        self.rb_copy_include.set_group(self.rb_copy_none)
        self.rb_copy_iso.set_active(True)  # Default to ISO customizations

        # Connect signal handlers
        self.rb_copy_none.connect("toggled", self._on_copy_option_changed)
        self.rb_copy_iso.connect("toggled", self._on_copy_option_changed)
        self.rb_copy_include.connect("toggled", self._on_copy_option_changed)

        box_copy.append(self.rb_copy_none)
        box_copy.append(self.rb_copy_iso)
        box_copy.append(self.rb_copy_include)

        # ISO customizations details
        iso_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        iso_info.set_margin_start(20)
        iso_label = Gtk.Label.new(
            "Tipp: Lege im Include-Ordner die gleiche Verzeichnisstruktur wie im Ziel an, alles wird 1:1 kopiert."
        )
        iso_label.set_wrap(True)
        iso_info.append(iso_label)
        box_copy.append(iso_info)

        # Include folder input
        include_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        include_box.set_margin_start(20)
        self.include_path = ""  # Store selected path
        self.btn_choose_folder = Gtk.Button.new_with_label("Ordner auswählen...")
        self.btn_choose_folder.set_sensitive(False)  # Disabled by default
        self.btn_choose_folder.connect("clicked", self._on_choose_folder_clicked)
        include_box.append(Gtk.Label.new("Pfad:"))
        include_box.append(self.btn_choose_folder)
        self.lbl_selected_path = Gtk.Label.new("Kein Ordner ausgewählt")
        self.lbl_selected_path.set_halign(Gtk.Align.START)
        self.lbl_selected_path.add_css_class("dim-label")
        include_box.append(self.lbl_selected_path)
        box_copy.append(include_box)

    def get_selected_mirror(self) -> str:
        txt = self.cmb_mirror.get_active_text() or ""
        return txt if txt else MIRRORS[0]

    def get_mirror_url(self) -> str:
        selected = self.get_selected_mirror()

        # Extract URL from selected text
        if " - " in selected:
            parts = selected.split(" - ", 1)
            if len(parts) == 2:
                url = parts[1].strip()
                # Remove trailing slash
                if url.endswith("/"):
                    url = url[:-1]
                return url

        # Fallback to default
        return "https://repo-default.voidlinux.org"

    def get_selected_packages(self) -> List[str]:
        pkgs: List[str] = []
        if self.cb_cinnamon.get_active():
            pkgs.extend(CINNAMON_SET)
            pkgs.extend(SERVICES_SET)
            pkgs.extend(BASE_SET)
            pkgs.extend(XORG_SET)
        if self.cb_xfce.get_active():
            pkgs.extend(XFCE_SET)
            pkgs.extend(SERVICES_SET)
            pkgs.extend(BASE_SET)
            pkgs.extend(XORG_SET)
        if self.cb_nvidia.get_active():
            pkgs.extend(BUNDLE_NVIDIA)
        if self.cb_printer.get_active():
            pkgs.extend(BUNDLE_PRINTER)
        if self.cb_pipewire.get_active():
            pkgs.extend(BUNDLE_PIPEWIRE)
        if self.cb_codecs.get_active():
            pkgs.extend(BUNDLE_NONFREE_CODECS)
        if self.cb_flatpak.get_active():
            pkgs.extend(BUNDLE_FLATPAK)
        if self.cb_iso_packages.get_active():
            iso_packages = self._get_live_system_packages()
            pkgs.extend(iso_packages)
        if self.cb_firefox.get_active():
            pkgs.extend(BUNDLE_FIREFOX_DE)
        if self.cb_vivaldi.get_active():
            pkgs.extend(BUNDLE_VIVALDI)
        if self.cb_evolution.get_active():
            pkgs.extend(BUNDLE_EVOLUTION)
        if self.cb_thunderbird.get_active():
            pkgs.extend(BUNDLE_THUNDERBIRD_DE)
        if self.cb_libre.get_active():
            pkgs.extend(BUNDLE_LIBREOFFICE_DE)
        if self.cb_calendar.get_active():
            pkgs.append(PKG_GNOME_CALENDAR)
        if self.cb_papers.get_active():
            pkgs.append(PKG_PAPERS)
        if self.cb_evince.get_active():
            pkgs.append(PKG_EVINCE)
        if self.cb_vlc.get_active():
            pkgs.append(PKG_VLC)
        if self.cb_rhythmbox.get_active():
            pkgs.append(PKG_RHYTHMBOX)
        if self.cb_kdenlive.get_active():
            pkgs.append(PKG_KDENLIVE)
        if self.cb_obs.get_active():
            pkgs.append(PKG_OBS)

        seen = set()
        out = []
        for p in pkgs:
            if p not in seen:
                out.append(p)
                seen.add(p)
        return out

    def get_include_root(self) -> str:
        return self.include_path.strip()

    def _on_copy_option_changed(self, button):
        # Handle selection changes
        if button == self.rb_copy_include:
            self.btn_choose_folder.set_sensitive(True)
        else:
            self.btn_choose_folder.set_sensitive(False)

    def _on_choose_folder_clicked(self, button):
        # Open folder chooser dialog
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Include-Root Ordner auswählen")
        dialog.select_folder(None, None, self._on_folder_selected)

    def _on_folder_selected(self, dialog, result):
        # Handle folder selection result"
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                self.include_path = folder.get_path()
                self.lbl_selected_path.set_text(self.include_path)
        except Exception as e:
            # User cancelled or error occurred
            pass

    def get_copy_option(self) -> str:
        if self.rb_copy_none.get_active():
            return "none"
        elif self.rb_copy_iso.get_active():
            return "iso"
        elif self.rb_copy_include.get_active():
            return "include"

    def _get_live_system_packages(self) -> List[str]:
        try:
            # Get all installed packages
            result = subprocess.run(
                ["xbps-query", "-m"], capture_output=True, text=True, check=True
            )

            packages = []
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line and line.startswith("ii"):
                    # Parse package name from xbps-query output
                    parts = line.split()
                    if len(parts) >= 2:
                        pkg_full = parts[1]
                        # Remove version and architecture information
                        pkg_name = pkg_full.rsplit("-", 2)[0]
                        packages.append(pkg_name)

            return packages

        except subprocess.CalledProcessError as e:
            print(f"Error getting live system packages: {e}")
            return []
        except FileNotFoundError:
            print("xbps-query not found, cannot get live system packages")
            return []
