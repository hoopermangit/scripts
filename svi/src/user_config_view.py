import gi

gi.require_version("Gtk", "4.0")
import re
from typing import Dict

from gi.repository import Gtk

__all__ = ["UserConfigView"]


class UserConfigView(Gtk.Box):
    # Page to configure username, hostname, password and root password

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for s in (
            self.set_margin_top,
            self.set_margin_bottom,
            self.set_margin_start,
            self.set_margin_end,
        ):
            s(6)

        title = Gtk.Label.new("Benutzerkonfiguration")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.START)
        self.append(title)

        info = Gtk.Label.new(
            "Lege einen Benutzer und Hostname für dein System an. "
            "Alle Felder sind erforderlich für die Installation."
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

        frm_user = Gtk.Frame(label="Benutzer & Host")
        frm_user.add_css_class("card")
        root.append(frm_user)

        box_user = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for s in (
            box_user.set_margin_top,
            box_user.set_margin_bottom,
            box_user.set_margin_start,
            box_user.set_margin_end,
        ):
            s(6)
        frm_user.set_child(box_user)

        row_hn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        hostname_label = Gtk.Label.new("Hostname:")
        hostname_label.set_xalign(0)
        hostname_label.set_hexpand(True)
        row_hn.append(hostname_label)
        self.entry_hostname = Gtk.Entry()
        self.entry_hostname.set_placeholder_text("z. B. voidbox")
        row_hn.append(self.entry_hostname)
        box_user.append(row_hn)

        row_un = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        username_label = Gtk.Label.new("Benutzername:")
        username_label.set_xalign(0)
        username_label.set_hexpand(True)
        row_un.append(username_label)
        self.entry_username = Gtk.Entry()
        self.entry_username.set_placeholder_text("z. B. alice")
        row_un.append(self.entry_username)
        box_user.append(row_un)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(12)
        separator.set_margin_bottom(8)
        box_user.append(separator)

        row_pw = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        password_label = Gtk.Label.new("Passwort:")
        password_label.set_xalign(0)
        password_label.set_hexpand(True)
        row_pw.append(password_label)
        self.entry_password = Gtk.Entry()
        self.entry_password.set_visibility(False)
        self.entry_password.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        self.entry_password.set_placeholder_text("Passwort")
        row_pw.append(self.entry_password)
        box_user.append(row_pw)

        row_pw_confirm = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        pw_confirm_label = Gtk.Label.new("Passwort wiederholen:")
        pw_confirm_label.set_xalign(0)
        pw_confirm_label.set_hexpand(True)
        row_pw_confirm.append(pw_confirm_label)
        self.entry_password_confirm = Gtk.Entry()
        self.entry_password_confirm.set_visibility(False)
        self.entry_password_confirm.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        self.entry_password_confirm.set_placeholder_text("Passwort bestätigen")
        row_pw_confirm.append(self.entry_password_confirm)
        box_user.append(row_pw_confirm)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(12)
        separator.set_margin_bottom(8)
        box_user.append(separator)

        row_root_pw = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        root_pw_label = Gtk.Label.new("Root-Passwort:")
        root_pw_label.set_xalign(0)
        root_pw_label.set_hexpand(True)
        row_root_pw.append(root_pw_label)
        self.entry_root_password = Gtk.Entry()
        self.entry_root_password.set_visibility(False)
        self.entry_root_password.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        self.entry_root_password.set_placeholder_text("Root-Passwort")
        row_root_pw.append(self.entry_root_password)
        box_user.append(row_root_pw)

        row_root_pw_confirm = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        root_pw_confirm_label = Gtk.Label.new("Root-Passwort wiederholen:")
        root_pw_confirm_label.set_xalign(0)
        root_pw_confirm_label.set_hexpand(True)
        row_root_pw_confirm.append(root_pw_confirm_label)
        self.entry_root_password_confirm = Gtk.Entry()
        self.entry_root_password_confirm.set_visibility(False)
        self.entry_root_password_confirm.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        self.entry_root_password_confirm.set_placeholder_text(
            "Root-Passwort bestätigen"
        )
        row_root_pw_confirm.append(self.entry_root_password_confirm)
        box_user.append(row_root_pw_confirm)

        hint_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        hint_frame = Gtk.Frame(label="")
        hint_frame.add_css_class("card")
        root.append(hint_frame)

        hint_text = Gtk.Label.new(
            "Hinweis:\n"
            "• Der Benutzer wird zur Gruppe 'wheel' hinzugefügt (sudo-Zugriff)\n"
            "• Root-Passwort ist separat vom Benutzer-Passwort\n"
            "• Hostname ist der Name deines Computers im Netzwerk\n"
            "• Nutze starke, einzigartige Passwörter für Sicherheit\n"
            "• Mindestens 6 Zeichen für alle Passwörter empfohlen"
        )
        hint_text.set_wrap(True)
        hint_text.set_halign(Gtk.Align.START)
        hint_text.set_use_markup(True)
        hint_box.append(hint_text)
        hint_frame.set_child(hint_box)

    def validate_user_input(self):
        # Validate required fields
        hostname = (self.entry_hostname.get_text() or "").strip()
        username = (self.entry_username.get_text() or "").strip()
        password = self.entry_password.get_text() or ""
        password_confirm = self.entry_password_confirm.get_text() or ""
        root_password = self.entry_root_password.get_text() or ""
        root_password_confirm = self.entry_root_password_confirm.get_text() or ""

        if not hostname:
            raise ValueError("Hostname ist erforderlich.")
        if not username:
            raise ValueError("Benutzername ist erforderlich.")
        if not password:
            raise ValueError("Benutzer-Passwort ist erforderlich.")
        if not root_password:
            raise ValueError("Root-Passwort ist erforderlich.")

        # Validate password matches
        if password != password_confirm:
            raise ValueError(
                "Das Benutzer Passwort stimmt nicht überein. Bitte überprüfe deine eingabe."
            )

        if root_password != root_password_confirm:
            raise ValueError(
                "Das Root Passwort stimmt nicht überein. Bitte überprüfe deine eingabe."
            )

        # Check if username is lowercase
        if username != username.lower():
            raise ValueError("Benutzername darf keine Großbuchstaben enthalten.")

        # Validate username format
        if not re.match(r"^[a-z][a-z0-9_-]*$", username):
            raise ValueError(
                "Benutzername darf nur Buchstaben, Zahlen, Unterstriche und Bindestriche enthalten und muss mit einem Buchstaben beginnen."
            )

        # Check maximum length
        if len(username) > 32:
            raise ValueError("Benutzername darf höchstens 32 Zeichen lang sein.")

        # Check for specific problematic patterns
        if username.startswith("-"):
            raise ValueError("Benutzername darf nicht mit einem Bindestrich beginnen.")

        if "--" in username:
            raise ValueError(
                "Benutzername darf keine aufeinanderfolgenden Bindestriche enthalten."
            )

        # Validate hostname format
        if not all(c.isalnum() or c in "-." for c in hostname):
            raise ValueError(
                "Hostname darf nur Buchstaben, Nummern, Bindestriche und Punkte enthalten."
            )

    def get_user_payload(self) -> Dict:
        # Returns user/host block with root password
        out: Dict[str, object] = {}
        hostname = (self.entry_hostname.get_text() or "").strip()
        username = (self.entry_username.get_text() or "").strip()
        password = (self.entry_password.get_text() or "").strip()
        password_confirm = self.entry_password_confirm.get_text() or ""
        root_password = self.entry_root_password.get_text() or ""
        root_password_confirm = self.entry_root_password_confirm.get_text() or ""

        out["hostname"] = hostname
        out["name"] = username.lower()  # Ensure username is lowercase
        out["password"] = password
        out["root_password"] = root_password

        # Add user groups
        if username:
            out["groups"] = [
                "lpadmin",  # Printing
                "bluetooth",  # Bluetooth access
                "audio",  # Audio devices
                "video",  # Video devices
                "optical",  # CD/DVD drives
                "storage",  # Storage devices
                "scanner",  # Scanner devices
                "network",  # Network management
                "plugdev",  # Pluggable devices
                "users",  # Regular users group
                "wheel",  # Wheel group for sudo access
            ]

        return out
