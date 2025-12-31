import gi
import re
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from translations import T

class UserConfigView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.set_margin_top(20)
        self.set_margin_start(20)
        self.set_margin_end(20)
        
        # Hostname
        self.entry_host = self._add_field(T("user_host"), "void-pc")
        
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        
        # User
        self.entry_user = self._add_field(T("user_name"), "user")
        self.entry_pw = self._add_field(T("user_pass"), is_pw=True)
        self.entry_pw2 = self._add_field(f"{T('user_pass')} (wdh.)", is_pw=True)
        
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        
        # Root
        self.entry_root = self._add_field(T("user_root"), is_pw=True)
        self.entry_root2 = self._add_field(f"{T('user_root')} (wdh.)", is_pw=True)

    def _add_field(self, label_text, placeholder="", is_pw=False):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        lbl = Gtk.Label(label=label_text, xalign=0)
        box.append(lbl)
        
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        if is_pw:
            entry.set_visibility(False)
            entry.set_input_purpose(Gtk.InputPurpose.PASSWORD)
            
        box.append(entry)
        self.append(box)
        return entry

    def validate_user_input(self):
        # Validierung
        user = self.entry_user.get_text()
        host = self.entry_host.get_text()
        
        if not user or not re.match(r"^[a-z_][a-z0-9_-]*$", user):
            raise ValueError(f"Ungültiger Benutzername: '{user}'. Bitte nur Kleinbuchstaben und Zahlen verwenden.")
            
        if not host:
            raise ValueError("Hostname darf nicht leer sein.")
        
        if self.entry_pw.get_text() != self.entry_pw2.get_text():
            raise ValueError("Benutzer-Passwörter stimmen nicht überein.")
            
        if not self.entry_pw.get_text():
            raise ValueError("Bitte ein Benutzer-Passwort vergeben.")
            
        if self.entry_root.get_text() != self.entry_root2.get_text():
            raise ValueError("Root-Passwörter stimmen nicht überein.")
            
        if not self.entry_root.get_text():
            raise ValueError("Bitte ein Root-Passwort vergeben.")

    def get_user_payload(self):
        return {
            "hostname": self.entry_host.get_text().strip(),
            "name": self.entry_user.get_text().strip(),
            "password": self.entry_pw.get_text(),
            "root_password": self.entry_root.get_text()
        }