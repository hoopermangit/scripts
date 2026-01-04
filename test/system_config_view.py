import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from translations import T

LANG_MAP = {
    "Español (es_PA.UTF-8)": "es_PA.UTF-8",
}

KEYMAPS = [
    ("Español (es)", "es"),
]

TIMEZONES = ["America/Panama"]

class SystemConfigView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_top(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

        # Titel & Beschreibung
        lbl_title = Gtk.Label(label=T("sys_title"), xalign=0)
        lbl_title.add_css_class("title-2")
        self.append(lbl_title)

        lbl_desc = Gtk.Label(label=T("sys_desc"), xalign=0, wrap=True)
        lbl_desc.set_margin_bottom(10)
        self.append(lbl_desc)

        # --- Frame: Region & Sprache ---
        frame_lang = Gtk.Frame(label=T("sys_region"))
        frame_lang.add_css_class("card")
        self.append(frame_lang)

        box_lang = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box_lang.set_margin_top(10); box_lang.set_margin_bottom(10)
        box_lang.set_margin_start(10); box_lang.set_margin_end(10)
        frame_lang.set_child(box_lang)

        # Zeile: Systemsprache
        row_lang = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row_lang.append(Gtk.Label(label=T("sys_lang"), xalign=0, hexpand=True))
        self.cmb_lang = Gtk.ComboBoxText()
        for l in LANG_MAP: self.cmb_lang.append_text(l)
        self.cmb_lang.set_active(0)
        row_lang.append(self.cmb_lang)
        box_lang.append(row_lang)

        # Zeile: Zeitzone
        row_tz = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row_tz.append(Gtk.Label(label=T("sys_tz"), xalign=0, hexpand=True))
        self.cmb_tz = Gtk.ComboBoxText()
        for t in TIMEZONES: self.cmb_tz.append_text(t)
        self.cmb_tz.set_active(0)
        row_tz.append(self.cmb_tz)
        box_lang.append(row_tz)

        # --- Frame: Tastatur ---
        frame_key = Gtk.Frame(label=T("sys_kbd_frame"))
        frame_key.add_css_class("card")
        self.append(frame_key)

        box_key = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box_key.set_margin_top(10); box_key.set_margin_bottom(10)
        box_key.set_margin_start(10); box_key.set_margin_end(10)
        frame_key.set_child(box_key)

        # Zeile: Layout
        row_key = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row_key.append(Gtk.Label(label=T("sys_layout"), xalign=0, hexpand=True))
        self.cmb_key = Gtk.ComboBoxText()
        for k, v in KEYMAPS: self.cmb_key.append_text(k)
        self.cmb_key.set_active(0)
        row_key.append(self.cmb_key)
        box_key.append(row_key)

    def get_selected_language(self):
        return LANG_MAP.get(self.cmb_lang.get_active_text(), "es_PA.UTF-8")

    def get_selected_keyboard_layout(self):
        txt = self.cmb_key.get_active_text()
        for k, v in KEYMAPS:
            if k == txt: return v
        return "es"

    def get_selected_timezone(self):
        return self.cmb_tz.get_active_text()
