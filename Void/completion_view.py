import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class CompletionView(Gtk.Box):
    def __init__(self, on_reboot, on_quit):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        
        icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
        icon.set_pixel_size(96)
        icon.add_css_class("success")
        self.append(icon)
        
        lbl = Gtk.Label(label="Installation successful!")
        lbl.add_css_class("title-1")
        self.append(lbl)
        
        lbl2 = Gtk.Label(label="The system is now ready.")
        self.append(lbl2)
        
        box_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box_btn.set_halign(Gtk.Align.CENTER)
        self.append(box_btn)
        
        btn_quit = Gtk.Button(label="Finish")
        btn_quit.connect("clicked", on_quit)
        box_btn.append(btn_quit)
        
        btn_reboot = Gtk.Button(label="Reboot")
        btn_reboot.add_css_class("suggested-action")
        btn_reboot.connect("clicked", on_reboot)
        box_btn.append(btn_reboot)
