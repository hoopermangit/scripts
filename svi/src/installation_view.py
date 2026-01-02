import gi

gi.require_version("Gtk", "4.0")
import os
import threading
from typing import Any, Dict, Optional

from gi.repository import GLib, Gtk

from installation_backend import InstallationBackend

TARGET_ROOT = "/mnt/void"


class InstallationView(Gtk.Box):
    # This page shows the installation progress
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, **kwargs, orientation=Gtk.Orientation.VERTICAL, spacing=8
        )
        for s in (
            self.set_margin_top,
            self.set_margin_bottom,
            self.set_margin_start,
            self.set_margin_end,
        ):
            s(6)

        title = Gtk.Label.new("Installation")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        self.append(title)

        # Installation steps
        self.steps = [
            {
                "id": "partitioning",
                "label": "1. Partitionen erstellen & formatieren",
                "status": "queued",
            },
            {
                "id": "mounting",
                "label": "2. Dateisysteme einhängen",
                "status": "queued",
            },
            {
                "id": "install_base",
                "label": "3. Basissystem und Pakete installieren",
                "status": "queued",
            },
            {
                "id": "copy_customizations",
                "label": "4. Anpassungen kopieren",
                "status": "queued",
            },
            {
                "id": "configure_system",
                "label": "5. System konfigurieren (fstab, Hostname, etc.)",
                "status": "queued",
            },
            {
                "id": "configure_bootloader",
                "label": "6. Bootloader (GRUB) installieren",
                "status": "queued",
            },
        ]

        # Steps list box
        self.steps_listbox = Gtk.ListBox()
        self.steps_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.steps_listbox.add_css_class("boxed-list")
        self.append(self.steps_listbox)
        self._build_steps_ui()

        # Log frame
        log_frame = Gtk.Frame(label="Log")
        log_frame.set_margin_top(8)
        self.append(log_frame)
        sc = Gtk.ScrolledWindow()
        sc.set_vexpand(True)
        sc.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sc.set_min_content_height(80)
        log_frame.set_child(sc)
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textbuffer = self.textview.get_buffer()
        sc.set_child(self.textview)

        # Initialize properties
        self.plan: Dict[str, Any] = {}
        self._worker: Optional[threading.Thread] = None
        self.target_root = TARGET_ROOT
        self._binds_active = False
        self.completion_callback = None

        # Initialize backend with logging callback
        self.backend = InstallationBackend(self.target_root, self._log)

    def _build_steps_ui(self):
        self._update_steps_ui()

    def _update_step_status(
        self, step_id: str, status: str, error_msg: Optional[str] = None
    ):
        # Update step status for the UI
        for step in self.steps:
            if step["id"] == step_id:
                step["status"] = status
                if error_msg:
                    step["error_msg"] = error_msg
                break

        self._update_steps_ui()

    def _update_steps_ui(self):
        # Update step status in the UI
        child = self.steps_listbox.get_first_child()
        while child:
            self.steps_listbox.remove(child)
            child = self.steps_listbox.get_first_child()

        # Rebuild UI with current status
        for step in self.steps:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            box.set_margin_top(8)
            box.set_margin_bottom(8)
            box.set_margin_start(12)
            box.set_margin_end(12)

            # Status icon
            status = step["status"]
            if status == "running":
                icon = "⏳"
                css_class = "warning"
            elif status == "success":
                icon = "✅"
                css_class = "success"
            elif status == "failure":
                icon = "❌"
                css_class = "error"
            else:
                icon = "⏸️"
                css_class = "dim-label"

            icon_label = Gtk.Label.new(icon)
            icon_label.add_css_class(css_class)
            box.append(icon_label)

            step_label = Gtk.Label.new(step["label"])
            step_label.set_halign(Gtk.Align.START)
            step_label.set_hexpand(True)
            if status == "running":
                step_label.add_css_class("warning")
            elif status == "success":
                step_label.add_css_class("success")
            elif status == "failure":
                step_label.add_css_class("error")
            box.append(step_label)

            # If we get an error, show the error message
            if status == "failure" and step.get("error_msg"):
                error_label = Gtk.Label.new(step["error_msg"])
                error_label.add_css_class("error")
                error_label.set_wrap(True)
                box.append(error_label)

            row.set_child(box)
            self.steps_listbox.append(row)

    def set_plan(self, plan: Dict[str, Any]):
        self.plan = plan or {}

    def start_installation(self):
        if self._worker and self._worker.is_alive():
            return
        self._worker = threading.Thread(target=self._run_install, daemon=True)
        self._worker.start()

    def set_completion_callback(self, callback):
        self.completion_callback = callback

    def _log(self, msg: str):
        def update_log():
            self.textbuffer.insert(self.textbuffer.get_end_iter(), msg + "\n")
            # Auto-scroll to bottom
            end_iter = self.textbuffer.get_end_iter()
            end_mark = self.textbuffer.create_mark(None, end_iter, False)
            self.textview.scroll_mark_onscreen(end_mark)
            self.textbuffer.delete_mark(end_mark)

        GLib.idle_add(update_log)

    def _run_install(self):
        current_step = ""
        try:
            os.makedirs(self.target_root, exist_ok=True)
            # Currently only supports erase disk as an option, but I will add more options soon
            mode = self.plan.get("mode", "erase")
            if mode != "erase":
                raise Exception(
                    f"Unbekannter Partitionierungsmodus: {mode}. Only 'erase' mode is supported."
                )

            current_step = "partitioning"
            GLib.idle_add(self._update_step_status, current_step, "running")
            # Always use erase mode for now
            assignments = self.backend._apply_auto_partitioning_erase(self.plan)
            self.plan["manual_partitions"] = assignments
            GLib.idle_add(self._update_step_status, current_step, "success")

            # Mount filesystems
            current_step = "mounting"
            GLib.idle_add(self._update_step_status, current_step, "running")
            self.backend._mount_filesystems(self.plan)
            GLib.idle_add(self._update_step_status, current_step, "success")

            # Install base system and packages
            current_step = "install_base"
            GLib.idle_add(self._update_step_status, current_step, "running")
            self.backend._configure_mirror(self.plan)
            self.backend._xbps_install(self.plan)
            GLib.idle_add(self._update_step_status, current_step, "success")

            # Copy the customizations that the user selected
            copy_option = self.plan.get("copy_option", "none")
            if copy_option == "iso":
                current_step = "copy_customizations"
                GLib.idle_add(self._update_step_status, current_step, "running")
                self.backend._copy_iso_customizations()
                GLib.idle_add(self._update_step_status, current_step, "success")
            elif copy_option == "include":
                include_root = self.plan.get("include_root", "")
                if include_root and os.path.exists(include_root):
                    current_step = "copy_customizations"
                    GLib.idle_add(self._update_step_status, current_step, "running")
                    self.backend._copy_include_root(include_root)
                    GLib.idle_add(self._update_step_status, current_step, "success")
            elif copy_option == "none":
                current_step = "copy_customizations"
                GLib.idle_add(self._update_step_status, current_step, "running")
                GLib.idle_add(self._update_step_status, current_step, "success")

            # Configure system
            current_step = "configure_system"
            GLib.idle_add(self._update_step_status, current_step, "running")
            self.backend._generate_fstab(self.plan)
            self.backend._configure_hostname(self.plan)
            self.backend._configure_locale_kbd(self.plan)
            self.backend._configure_timezone(self.plan)
            self.backend._configure_user(self.plan)
            self.backend._enable_services(self.plan)
            self.backend._configure_pipewire(self.plan)
            self.backend._configure_flatpak(self.plan)
            GLib.idle_add(self._update_step_status, current_step, "success")

            # Install bootloader
            current_step = "configure_bootloader"
            GLib.idle_add(self._update_step_status, current_step, "running")
            self.backend._install_bootloader(self.plan)
            GLib.idle_add(self._update_step_status, current_step, "success")

            self._log("\n=== INSTALLATION ERFOLGREICH ABGESCHLOSSEN ===")
            # Notify completion if callback is set
            if self.completion_callback:
                GLib.idle_add(self.completion_callback, True)

        except Exception as e:
            self._log(f"\n--- FATALER FEHLER BEI SCHRITT '{current_step}' ---")
            self._log(str(e))
            GLib.idle_add(self._update_step_status, current_step, "failure", str(e))
            # Notify completion with failure
            if self.completion_callback:
                GLib.idle_add(self.completion_callback, False)
        finally:
            self.backend._leave_chroot_mounts()
