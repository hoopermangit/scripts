import gi

gi.require_version("Gtk", "4.0")
from typing import Dict

from gi.repository import Gtk

__all__ = ["SystemConfigView"]

LANG_MAP = {
    "Español (es_PA.UTF-8)": "es_PA.UTF-8",
}

KEYBOARD_LAYOUTS = [
    ("Español (es)", "es"),
]

TIMEZONES = [
    "America/Panama",
    "UTC",
]


class SystemConfigView(Gtk.Box):
    # Page to select language, timezone and keyboard layout

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for s in (
            self.set_margin_top,
            self.set_margin_bottom,
            self.set_margin_start,
            self.set_margin_end,
        ):
            s(6)

        title = Gtk.Label.new("Systemkonfiguration")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.START)
        self.append(title)

        info = Gtk.Label.new(
            "Wähle deine Systemeinstellungen für Sprache, Zeitzone und Tastatur-Layout."
        )
        info.set_wrap(True)
        info.set_halign(Gtk.Align.START)
        self.append(info)

        sc = Gtk.ScrolledWindow()
        sc.set_vexpand(True)
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.append(sc)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        sc.set_child(root)

        frm_lang = Gtk.Frame(label="Region & Sprache")
        frm_lang.add_css_class("card")
        root.append(frm_lang)

        box_lang = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for s in (
            box_lang.set_margin_top,
            box_lang.set_margin_bottom,
            box_lang.set_margin_start,
            box_lang.set_margin_end,
        ):
            s(6)
        frm_lang.set_child(box_lang)

        row_lang = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lang_label = Gtk.Label.new("Systemsprache:")
        lang_label.set_xalign(0)
        lang_label.set_hexpand(True)
        row_lang.append(lang_label)
        self.cmb_language = Gtk.ComboBoxText()
        for disp in LANG_MAP.keys():
            self.cmb_language.append_text(disp)
        try:
            self.cmb_language.set_active(
                list(LANG_MAP.keys()).index("Español (es_PA.UTF-8)")
            )
        except ValueError:
            self.cmb_language.set_active(0)
        row_lang.append(self.cmb_language)
        box_lang.append(row_lang)

        row_tz = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        tz_label = Gtk.Label.new("Zeitzone:")
        tz_label.set_xalign(0)
        tz_label.set_hexpand(True)
        row_tz.append(tz_label)
        self.cmb_timezone = Gtk.ComboBoxText()
        for tz in TIMEZONES:
            self.cmb_timezone.append_text(tz)
        try:
            self.cmb_timezone.set_active(TIMEZONES.index("America/Panama"))
        except ValueError:
            self.cmb_timezone.set_active(0)
        row_tz.append(self.cmb_timezone)
        box_lang.append(row_tz)

        frm_kbd = Gtk.Frame(label="Tastatur")
        frm_kbd.add_css_class("card")
        root.append(frm_kbd)

        box_kbd = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for s in (
            box_kbd.set_margin_top,
            box_kbd.set_margin_bottom,
            box_kbd.set_margin_start,
            box_kbd.set_margin_end,
        ):
            s(6)
        frm_kbd.set_child(box_kbd)

        kbd_label = Gtk.Label.new("Layout:")
        kbd_label.set_xalign(0)
        kbd_label.set_hexpand(True)
        box_kbd.append(kbd_label)
        self.cmb_kbd = Gtk.ComboBoxText()
        for disp, _code in KEYBOARD_LAYOUTS:
            self.cmb_kbd.append_text(disp)
        self.cmb_kbd.set_active(0)
        box_kbd.append(self.cmb_kbd)

    def get_selected_language(self) -> str:
        disp = self.cmb_language.get_active_text() or ""
        return LANG_MAP.get(disp, "es_PA.UTF-8")

    def get_selected_timezone(self) -> str:
        return self.cmb_timezone.get_active_text() or "America/Panama"

    def get_selected_keyboard_layout(self) -> str:
        disp = self.cmb_kbd.get_active_text() or ""
        for d, code in KEYBOARD_LAYOUTS:
            if d == disp:
                return code
        return "es"
