import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from translations import T

class WelcomeView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_margin_top(40)
        self.set_margin_bottom(40)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("system-installer")
        icon.set_pixel_size(128)
        self.append(icon)
        
        # Titel (Übersetzt)
        title = Gtk.Label(label=T("wel_title"))
        title.add_css_class("title-1")
        self.append(title)
        
        # Beschreibung (Übersetzt)
        desc = Gtk.Label(label=T("wel_desc"))
        desc.set_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.set_max_width_chars(50)
        self.append(desc)