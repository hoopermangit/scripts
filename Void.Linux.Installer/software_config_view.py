import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

# SOFTWARE-LISTE
CATEGORIES = {
    "System & Hardware": [
        ("meta:printer", "Drucker-Support (CUPS)"),
        ("meta:flatpak", "Flatpak Support"),
        ("meta:nvidia", "Nvidia Treiber (Non-Free)"),
    ],
    "Office": [
        ("flatpak:org.onlyoffice.desktopeditors", "OnlyOffice (Flatpak)"),
        ("xbps:libreoffice", "LibreOffice"),
        ("xbps:libreoffice-i18n-de", "LibreOffice (DE)"),
        ("xbps:papers", "Papers (PDF)"),
        ("xbps:gnome-calendar", "GNOME Kalender"),
        ("xbps:gnome-calculator", "Taschenrechner"),
    ],
    "Internet": [
        ("xbps:firefox", "Firefox"),
        ("xbps:firefox-i18n-de", "Firefox (DE)"),
        ("xbps:chromium", "Chromium"),
        ("xbps:vivaldi", "Vivaldi (Non-Free)"),
        ("xbps:thunderbird", "Thunderbird"),
        ("xbps:thunderbird-i18n-de", "Thunderbird (DE)"),
        ("xbps:evolution", "Evolution"),
    ],
    "Multimedia": [
        ("xbps:vlc", "VLC Media Player"),
        ("xbps:mpv", "MPV Player"),
        ("xbps:rhythmbox", "Rhythmbox"),
        ("xbps:obs", "OBS Studio"),
    ],
    "Grafik": [
        ("xbps:gimp", "GIMP"),
        ("xbps:inkscape", "Inkscape"),
        ("xbps:gnome-photos", "GNOME Photos"),
        ("xbps:gthumb", "gThumb"),
    ]
}

class SoftwareConfigView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(20)
        self.set_margin_end(20)
        
        self.append(Gtk.Label(label="Zusätzliche Software wählen (Internet erforderlich):", xalign=0))
        
        sc = Gtk.ScrolledWindow()
        sc.set_vexpand(True)
        self.append(sc)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sc.set_child(content)
        
        self.checks = {}
        
        for cat, items in CATEGORIES.items():
            frame = Gtk.Frame(label=cat)
            frame.add_css_class("card")
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            box.set_margin_top(5)
            box.set_margin_bottom(5)
            box.set_margin_start(10)
            frame.set_child(box)
            
            for id_str, label in items:
                chk = Gtk.CheckButton(label=label)
                self.checks[id_str] = chk
                box.append(chk)
            
            content.append(frame)

    def get_selected_packages(self):
        selected = []
        for pid, chk in self.checks.items():
            if chk.get_active():
                selected.append(pid)
        
        # Auto-Dependency: Flatpak App erfordert Flatpak Support
        has_flatpak_app = any(x.startswith("flatpak:") for x in selected)
        if has_flatpak_app and "meta:flatpak" not in selected:
            selected.append("meta:flatpak")
            
        return selected