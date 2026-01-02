import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk


class CompletionView(Gtk.Box):
    # This page shows that the installation is completed
    def __init__(self, on_restart_callback, on_exit_callback):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.set_homogeneous(False)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_margin_top(50)
        self.set_margin_bottom(50)
        self.set_margin_start(50)
        self.set_margin_end(50)

        self._on_restart_callback = on_restart_callback
        self._on_exit_callback = on_exit_callback

        self._setup_ui()

    def _setup_ui(self):
        title_label = Gtk.Label.new()
        title_label.set_markup(
            "<span font_desc='Sans Bold 24'>Installation erfolgreich abgeschlossen!</span>"
        )
        title_label.set_halign(Gtk.Align.CENTER)
        self.append(title_label)
        message_label = Gtk.Label(
            label="Das Void Linux System wurde erfolgreich auf Ihrem Computer installiert.\n"
            + "Sie können das System jetzt neu starten, um es zu nutzen."
        )
        message_label.set_halign(Gtk.Align.CENTER)
        self.append(message_label)
        self.append(Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30))
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)
        restart_button = Gtk.Button(label="System neu starten")
        restart_button.add_css_class("suggested-action")
        restart_button.connect("clicked", self._on_restart_callback)
        button_box.append(restart_button)
        exit_button = Gtk.Button(label="Installer beenden")
        exit_button.connect("clicked", self._on_exit_callback)
        button_box.append(exit_button)

        self.append(button_box)
