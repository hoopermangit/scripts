#!/usr/bin/env python3

import importlib.util
import os
import subprocess
import sys

import gi

HERE = os.path.dirname(os.path.realpath(__file__))

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk


def show_root_warning_and_exit():
    # Show no root error dialog

    from gi.repository import Gdk

    # Check if display is avaible
    display = Gdk.Display.get_default()
    if display is not None:
        # Create a gtk application for the dialog
        app = Gtk.Application(application_id="org.svi.rootcheck")

        def on_activate(app):
            # Create a temporary window for the dialog
            temp_window = Gtk.Window(application=app)
            temp_window.set_title("svi - Root Check")

            dialog = Gtk.MessageDialog(
                transient_for=temp_window,
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.CLOSE,
                text="Root-Berechtigungen erforderlich",
            )
            dialog.set_property(
                "secondary-text",
                "Svi muss als root ausgeführt werden. Bitte starte das Programm mit 'sudo' oder als root-Benutzer.",
            )

            def on_response(dialog, response_id):
                dialog.destroy()
                app.quit()

            dialog.connect("response", on_response)
            dialog.present()

        app.connect("activate", on_activate)
        app.run([])

        sys.exit(1)
    else:
        # Fallback: print to console if no GUI available
        print("ERROR: Root-Berechtigungen erforderlich")
        print("Svi muss als root ausgeführt werden.")
        print("Bitte starte das Programm mit 'sudo' oder als root-Benutzer.")
        sys.exit(1)


def _import_view(mod_basename: str, class_name: str):
    # Import function for Nuitka
    try:
        # Try to import the module directly
        mod = importlib.import_module(mod_basename)
        return getattr(mod, class_name)
    except ImportError:
        # Fallback: try relative import
        try:
            mod = importlib.import_module(f".{mod_basename}", package="src")
            return getattr(mod, class_name)
        except ImportError:
            pass
        raise ImportError(f"Could not import {class_name} from {mod_basename}")


def check_root_privileges():
    # Check if we have root permissions
    if os.geteuid() != 0:
        show_root_warning_and_exit()


WelcomeView = _import_view("welcome_view", "WelcomeView")
SystemConfigView = _import_view("system_config_view", "SystemConfigView")
UserConfigView = _import_view("user_config_view", "UserConfigView")
PartitioningView = _import_view("partitioning_view", "PartitioningView")
SoftwareConfigView = _import_view("software_config_view", "SoftwareConfigView")
SummaryView = _import_view("summary_view", "SummaryView")
InstallationView = _import_view("installation_view", "InstallationView")
CompletionView = _import_view("completion_view", "CompletionView")


class InstallerApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="org.svi.App",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.window: Gtk.ApplicationWindow | None = None
        self.stack: Gtk.Stack | None = None
        self.view_welcome: WelcomeView | None = None
        self.view_system_config: SystemConfigView | None = None
        self.view_user_config: UserConfigView | None = None
        self.view_part: PartitioningView | None = None
        self.view_software: SoftwareConfigView | None = None
        self.view_summary: SummaryView | None = None
        self.view_install: InstallationView | None = None
        self.view_done: CompletionView | None = None
        self.btn_back: Gtk.Button | None = None
        self.btn_next: Gtk.Button | None = None
        self.current_plan: dict = {}
        self.current_page: str = "welcome"

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        if not self.window:
            self._load_css()
            self._build_ui()
            self._build_views()
        self.window.present()

    def _load_css(self):
        css_provider = Gtk.CssProvider()
        app_dir = os.path.dirname(os.path.abspath(__file__))
        css_file = os.path.join(app_dir, "ui.css")
        if os.path.exists(css_file):
            try:
                css_provider.load_from_path(css_file)
                display = Gdk.Display.get_default()
                Gtk.StyleContext.add_provider_for_display(
                    display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                print("ui.css erfolgreich geladen und angewendet.")
            except Exception as e:
                print(f"Fehler beim Laden von ui.css: {e}")
        else:
            print("Warnung: ui.css wurde nicht im Anwendungsverzeichnis gefunden.")

    def _build_ui(self):
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("Simple Void Installer")
        self.window.set_default_size(900, 650)
        self.window.set_size_request(600, 350)
        self.window.set_resizable(True)

        # Create content area with navigation and stack switcher
        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.stack.connect("notify::visible-child-name", self._on_stack_changed)

        # Navigation controls in a toolbar below title
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        toolbar.set_margin_top(6)
        toolbar.set_margin_bottom(6)
        toolbar.set_margin_start(8)
        toolbar.set_margin_end(8)

        # Add step indicator
        self.step_label = Gtk.Label.new("")
        self.step_label.add_css_class("title-4")
        self.step_label.set_halign(Gtk.Align.CENTER)
        self.step_label.set_hexpand(True)
        toolbar.append(self.step_label)

        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.btn_back = Gtk.Button.new_with_label("Zurück")
        self.btn_back.connect("clicked", self.on_back)
        self.btn_next = Gtk.Button.new_with_label("Weiter")
        self.btn_next.connect("clicked", self.on_next)
        nav_box.append(self.btn_back)
        nav_box.append(self.btn_next)
        toolbar.append(nav_box)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.append(toolbar)
        content.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        content.append(self.stack)
        self.window.set_child(content)

    def _build_views(self):
        assert self.stack is not None

        def add_page(view, name, title):
            self.stack.add_titled(view, name, title)
            return view

        self.view_welcome = add_page(WelcomeView(), "welcome", "Willkommen")
        self.view_system_config = add_page(
            SystemConfigView(), "system_config", "Systemkonfiguration"
        )
        self.view_user_config = add_page(
            UserConfigView(), "user_config", "Benutzerkonfiguration"
        )
        self.view_part = add_page(PartitioningView(), "partition", "Partitionierung")
        self.view_software = add_page(SoftwareConfigView(), "software", "Software")
        self.view_summary = add_page(SummaryView(), "summary", "Zusammenfassung")
        self.view_install = add_page(InstallationView(), "install", "Installation")
        # Set completion callback for installation view
        self.view_install.set_completion_callback(self._on_installation_completed)
        self.view_done = add_page(
            CompletionView(
                on_restart_callback=self._on_restart_requested,
                on_exit_callback=self._on_exit_requested,
            ),
            "done",
            "Fertig",
        )
        self.stack.set_visible_child_name("welcome")
        self._update_nav_for("welcome")
        self._update_step_indicator("welcome")

    def _on_stack_changed(self, *_):
        if not self.stack:
            return
        name = self.stack.get_visible_child_name()
        if name:
            self.current_page = name
            self._update_nav_for(name)
            self._update_step_indicator(name)

    def _update_nav_for(self, page: str):
        if not (self.btn_back and self.btn_next):
            return
        order = [
            "welcome",
            "system_config",
            "user_config",
            "partition",
            "software",
            "summary",
            "install",
            "done",
        ]
        self.btn_back.set_visible(True)
        self.btn_next.set_visible(True)
        self.btn_back.set_sensitive(True)
        self.btn_next.set_sensitive(True)
        self.btn_next.remove_css_class("suggested-action")

        if page in ("welcome", "install", "done"):
            self.btn_back.set_visible(False)
        else:
            self.btn_back.set_sensitive(page in order[1:7])

        if page in ["welcome", "system_config", "user_config", "partition", "software"]:
            self.btn_next.set_label("Weiter")
            self.btn_next.add_css_class("suggested-action")
        elif page == "summary":
            self.btn_next.set_label("Installieren")
            self.btn_next.add_css_class("suggested-action")
        elif page == "install":
            self.btn_next.set_label("Weiter")
            self.btn_next.set_sensitive(False)
        elif page == "done":
            self.btn_next.set_visible(False)
        else:
            self.btn_next.set_label("Weiter")
            self.btn_next.add_css_class("suggested-action")

    def _update_step_indicator(self, page: str):
        # Show current step
        if not hasattr(self, "step_label"):
            return

        step_info = {
            "welcome": "Schritt 1/8: Willkommen",
            "system_config": "Schritt 2/8: Systemkonfiguration",
            "user_config": "Schritt 3/8: Benutzerkonfiguration",
            "partition": "Schritt 4/8: Partitionierung",
            "software": "Schritt 5/8: Software-Auswahl",
            "summary": "Schritt 6/8: Zusammenfassung",
            "install": "Schritt 7/8: Installation",
            "done": "Schritt 8/8: Abgeschlossen",
        }

        step_text = step_info.get(page, "")
        self.step_label.set_text(step_text)

    def _on_installation_completed(self, success: bool = True):
        if success:
            self.btn_next.set_sensitive(True)
            self.btn_next.set_label("Fertigstellen")
            self.btn_next.add_css_class("suggested-action")

    def on_back(self, *_):
        if not self.stack:
            return
        order = [
            "welcome",
            "system_config",
            "user_config",
            "partition",
            "software",
            "summary",
            "install",
            "done",
        ]
        if self.current_page in order:
            idx = order.index(self.current_page)
            if idx > 0 and self.current_page not in ("install", "done"):
                self.stack.set_visible_child_name(order[idx - 1])

    def on_next(self, *_):
        if not self.stack:
            return
        page = self.current_page
        if page == "welcome":
            self.stack.set_visible_child_name("system_config")
        elif page == "system_config":
            self.stack.set_visible_child_name("user_config")
        elif page == "user_config":
            try:
                if self.view_user_config:
                    self.view_user_config.validate_user_input()
                self.stack.set_visible_child_name("partition")
            except ValueError as e:
                self._show_warning(str(e))
                return
        elif page == "partition":
            try:
                if self.view_part:
                    self.view_part.validate_plan()
                self.stack.set_visible_child_name("software")
            except ValueError as e:
                self._show_warning(str(e))
                return
        elif page == "software":
            ok = self._rebuild_plan_preview_safe()
            self.stack.set_visible_child_name("summary")
            if not ok:
                self._show_warning(
                    "Einige Angaben konnten nicht übernommen werden.\nBitte prüfe die Felder."
                )
        elif page == "summary":
            self._show_installation_confirmation()
        elif page == "install":
            self.stack.set_visible_child_name("done")

    def _rebuild_plan_preview_safe(self) -> bool:
        try:
            plan = self._collect_plan()
            self.current_plan = plan
            if self.view_summary:
                filesystem_display = "Manuell zugewiesen"
                if plan.get("mode") in ("erase", "dual"):
                    auto_layout = plan.get("auto_layout", {}) or {}
                    filesystem_display = auto_layout.get(
                        "filesystem", "Nicht festgelegt"
                    )
                # Format user info without showing password
                user_info = plan.get("user")
                user_display = "(kein Benutzer konfiguriert)"
                if user_info:
                    parts = []
                    if user_info.get("name"):
                        parts.append(f"Name: {user_info['name']}")
                    if user_info.get("hostname"):
                        parts.append(f"Hostname: {user_info['hostname']}")
                    if user_info.get("password"):
                        parts.append("Passwort: ***")

                    if user_info.get("groups"):
                        parts.append(f"Gruppen: {', '.join(user_info['groups'])}")
                    user_display = (
                        "; ".join(parts) if parts else "Benutzer konfiguriert"
                    )

                self.view_summary.update_summary_data(
                    {
                        "Sprache": plan.get("language"),
                        "Zeitzone": plan.get("timezone"),
                        "Tastatur": plan.get("keyboard"),
                        "Zielgerät": plan.get("device") or "(keins gewählt)",
                        "Modus": plan.get("mode"),
                        "Dateisystem": filesystem_display,
                        "UEFI": "ja" if plan.get("uefi") else "nein",
                        "Benutzer": user_display,
                        "Pakete": ", ".join(plan.get("software") or []) or "(keine)",
                    }
                )
            return True
        except Exception as e:
            if self.view_summary:
                self.view_summary.update_summary_data(
                    {"Hinweis": f"Plan konnte nicht aufgebaut werden: {e}"}
                )
            return False

    def _collect_plan(self) -> dict:
        if not (
            self.view_welcome
            and self.view_system_config
            and self.view_user_config
            and self.view_part
            and self.view_software
        ):
            return {}
        part_plan = self.view_part.get_plan()
        user_payload = self.view_user_config.get_user_payload()
        return {
            **part_plan,
            "language": self.view_system_config.get_selected_language(),
            "timezone": self.view_system_config.get_selected_timezone(),
            "keyboard": self.view_system_config.get_selected_keyboard_layout(),
            "mirror_url": self.view_software.get_mirror_url(),
            "software": self.view_software.get_selected_packages(),
            "include_root": self.view_software.get_include_root(),
            "copy_option": self.view_software.get_copy_option(),
            "user": user_payload or None,
        }

    def _start_installation_now(self):
        plan = self.current_plan or self._collect_plan()
        if not self.view_install:
            return
        self.view_install.set_plan(plan)
        self.stack.set_visible_child_name("install")
        self._update_nav_for("install")
        GLib.idle_add(
            lambda: (self.view_install.start_installation(), GLib.SOURCE_REMOVE)[1]
        )

    def _show_installation_confirmation(self):
        # Confirm to start the Installation
        win = self.window or self.get_active_window()
        if isinstance(win, Gtk.ApplicationWindow):
            dlg = Gtk.MessageDialog(
                transient_for=win,
                modal=True,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.NONE,
                text="Installation starten?",
                secondary_text=(
                    "Möchtest du die Installation wirklich starten?\n\n"
                    "Dies wird die Festplatte verändern und kann Daten löschen. "
                    "Bitte stelle sicher, dass du deine Daten gesichert hast."
                ),
            )
            dlg.add_button("Nein", Gtk.ResponseType.NO)
            dlg.add_button("Ja", Gtk.ResponseType.YES)
            dlg.set_default_response(Gtk.ResponseType.NO)
            dlg.connect("response", self._on_installation_confirmed)
            dlg.present()

    def _on_installation_confirmed(self, dialog: Gtk.MessageDialog, response: int):
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            self._start_installation_now()

    def _on_restart_requested(self, *_):
        try:
            # Show confirmation dialog
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE,
                text="System neu starten?",
                secondary_text="Das System wird jetzt neu gestartet. Alle ungespeicherten Daten gehen verloren.",
            )
            dialog.add_button("Nein", Gtk.ResponseType.NO)
            dialog.add_button("Ja", Gtk.ResponseType.YES)
            dialog.set_default_response(Gtk.ResponseType.NO)

            def on_response(dialog, response):
                dialog.destroy()
                if response == Gtk.ResponseType.YES:
                    # Unmount any remaining filesystems
                    subprocess.run(["umount", "-R", "/mnt/void"], check=False)
                    # Restart system
                    subprocess.run(["reboot"], check=False)

            dialog.connect("response", on_response)
            dialog.present()
        except Exception as e:
            print(f"Restart failed: {e}")
            # restart installer if system restart fails
            self.current_plan = {}
            if self.stack:
                self.stack.set_visible_child_name("welcome")
                self._update_nav_for("welcome")

    def _on_exit_requested(self, *_):
        self.quit()

    def _show_warning(self, text: str):
        win = self.window or self.get_active_window()
        if isinstance(win, Gtk.ApplicationWindow):
            dlg = Gtk.MessageDialog(
                transient_for=win,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Hinweis",
                secondary_text=text,
            )
            dlg.connect("response", lambda d, r: d.destroy())
            dlg.present()


def main():
    check_root_privileges()
    app = InstallerApp()
    app.run([])


if __name__ == "__main__":
    main()
