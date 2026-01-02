import gi

gi.require_version("Gtk", "4.0")
from typing import Dict

from gi.repository import Gtk

__all__ = ["WelcomeView"]


class WelcomeView(Gtk.Box):
    # Page to show some information about the installer and installation steps

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        sc = Gtk.ScrolledWindow()
        sc.set_vexpand(True)
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for s in (
            container.set_margin_top,
            container.set_margin_bottom,
            container.set_margin_start,
            container.set_margin_end,
        ):
            s(6)

        title = Gtk.Label.new("Willkommen zum Simple Void Installer")
        title.add_css_class("title-1")
        title.set_halign(Gtk.Align.CENTER)
        container.append(title)

        intro_text = Gtk.Label.new(
            "Svi führt dich durch die Installation von Void Linux auf deinem Computer."
        )
        intro_text.set_wrap(True)
        intro_text.set_halign(Gtk.Align.CENTER)
        intro_text.add_css_class("body")
        container.append(intro_text)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(20)
        separator.set_margin_bottom(20)
        container.append(separator)

        steps_frame = Gtk.Frame(label="Installationsschritte")
        steps_frame.add_css_class("card")
        container.append(steps_frame)

        steps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for s in (
            steps_box.set_margin_top,
            steps_box.set_margin_bottom,
            steps_box.set_margin_start,
            steps_box.set_margin_end,
        ):
            s(20)
        steps_frame.set_child(steps_box)

        steps_label = Gtk.Label.new(
            "Die Installation besteht aus den folgenden Schritten:\n\n"
            "1. Systemkonfiguration: Sprache, Zeitzone und Tastatur einstellen\n"
            "2. Benutzeranlage: Systembenutzer und Passwörter konfigurieren\n"
            "3. Partitionierung: Festplatten partitionieren und formatieren\n"
            "4. Software-Auswahl: Pakete und zusätzliche Software auswählen\n"
            "5. Zusammenfassung: Installationseinstellungen überprüfen\n"
            "6. Installation: System installieren und konfigurieren"
        )
        steps_label.set_wrap(True)
        steps_label.set_halign(Gtk.Align.START)
        steps_label.add_css_class("body")
        steps_box.append(steps_label)

        warnings_frame = Gtk.Frame(label="Hinweise")
        warnings_frame.add_css_class("card")
        container.append(warnings_frame)

        warnings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for s in (
            warnings_box.set_margin_top,
            warnings_box.set_margin_bottom,
            warnings_box.set_margin_start,
            warnings_box.set_margin_end,
        ):
            s(20)
        warnings_frame.set_child(warnings_box)

        warnings_label = Gtk.Label.new(
            "Datenverlust: Die Installation wird die Festplatte formatieren. "
            "Alle Daten auf der Festplatte gehen verloren!\n\n"
            "Backup: Erstelle ein Backup wichtiger Daten vor der Installation.\n\n"
            "Strom: Stelle sicher, dass der Computer während der Installation "
            "mit Strom versorgt ist.\n\n"
            "Internet: Eine Internetverbindung wird für die Paketinstallation benötigt."
        )
        warnings_label.set_wrap(True)
        warnings_label.set_halign(Gtk.Align.START)
        warnings_label.add_css_class("body")
        warnings_box.append(warnings_label)

        sc.set_child(container)
        self.append(sc)
