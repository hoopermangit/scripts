import gi
import re

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
import json
import os
import subprocess
from typing import List, Dict, Any, Optional

FS_CHOICES = ["ext4", "btrfs", "xfs"]
BTRFS_DEFAULT_SUBVOLS = [
    ("@", "/", True),
    ("@home", "/home", True),
    ("@snapshots", "/.snapshots", True),
    ("@var_log", "/var/log", True),
]


class PartitioningView(Gtk.Box):
    # Page to select hard drive, file system etc.
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for s in (
            self.set_margin_top,
            self.set_margin_bottom,
            self.set_margin_start,
            self.set_margin_end,
        ):
            s(6)
        self.is_uefi = os.path.isdir("/sys/firmware/efi")

        # --- State ---
        self.disks: List[Dict[str, Any]] = []
        self.selected_disk: Optional[str] = None
        self.mode: str = "erase"
        self.fs_choice: str = "ext4"
        self.subvol_rows = []
        self.use_separate_home: bool = False
        self.home_size_percent: int = 50
        self.use_swap_partition: bool = False
        self.swap_partition_gib: int = 8
        self.esp_size_mib: int = 512

        title = Gtk.Label.new("Festplatten-Partitionierung")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        self.append(title)
        sc = Gtk.ScrolledWindow()
        sc.set_vexpand(True)
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.append(sc)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sc.set_child(main_box)
        disk_frame = Gtk.Frame(label="1. Ziel-Datenträger auswählen")
        disk_frame.add_css_class("card")
        main_box.append(disk_frame)
        disk_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        disk_box.set_margin_top(8)
        disk_box.set_margin_bottom(8)
        disk_box.set_margin_start(12)
        disk_box.set_margin_end(12)
        disk_frame.set_child(disk_box)
        disk_box.append(Gtk.Label.new("Festplatte:"))
        self.device_combo = Gtk.ComboBoxText()
        self.device_combo.connect("changed", self._on_device_changed)
        disk_box.append(self.device_combo)
        mode_frame = Gtk.Frame(label="2. Partitionierungs-Modus wählen")
        mode_frame.add_css_class("card")
        main_box.append(mode_frame)
        mode_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        mode_box.set_margin_top(8)
        mode_box.set_margin_bottom(8)
        mode_box.set_margin_start(12)
        mode_box.set_margin_end(12)
        mode_frame.set_child(mode_box)
        self.rb_erase = Gtk.CheckButton.new_with_label(
            "Automatisch: Gesamte Festplatte verwenden"
        )
        self.rb_erase.set_active(True)
        self.rb_erase.connect("toggled", self._on_mode_changed)
        mode_box.append(self.rb_erase)
        self.auto_options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        main_box.append(self.auto_options_box)
        layout_frame = Gtk.Frame(
            label="3. Layout-Optionen für automatische Einrichtung"
        )
        layout_frame.add_css_class("card")
        self.auto_options_box.append(layout_frame)
        layout_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        layout_box.set_margin_top(8)
        layout_box.set_margin_bottom(8)
        layout_box.set_margin_start(12)
        layout_box.set_margin_end(12)
        layout_frame.set_child(layout_box)
        row_fs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row_fs.append(Gtk.Label.new("Dateisystem:"))
        self.fs_combo = Gtk.ComboBoxText()
        for fs in FS_CHOICES:
            self.fs_combo.append_text(fs)
        self.fs_combo.set_active(FS_CHOICES.index("ext4"))
        self.fs_combo.connect("changed", self._on_fs_changed)
        row_fs.append(self.fs_combo)
        layout_box.append(row_fs)
        layout_box.append(
            Gtk.Separator(
                orientation=Gtk.Orientation.HORIZONTAL, margin_top=5, margin_bottom=5
            )
        )
        self.home_options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.cb_home = Gtk.CheckButton.new_with_label("Eigene /home Partition anlegen")
        self.cb_home.connect("toggled", self._on_home_toggled)
        self.home_options_box.append(self.cb_home)
        row_home_size = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row_home_size.append(Gtk.Label.new("Größe für /home (% des freien Platzes):"))
        self.spin_home_percent = Gtk.SpinButton.new_with_range(5, 95, 5)
        self.spin_home_percent.set_value(self.home_size_percent)
        self.spin_home_percent.connect("value-changed", self._on_home_percent_changed)
        row_home_size.append(self.spin_home_percent)
        self.home_options_box.append(row_home_size)
        layout_box.append(self.home_options_box)
        self.cb_swap_part = Gtk.CheckButton.new_with_label("Swap-Partition anlegen")
        self.cb_swap_part.connect("toggled", self._on_swap_part_toggled)
        layout_box.append(self.cb_swap_part)
        self.row_swap_size = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.row_swap_size.append(Gtk.Label.new("Größe der Swap-Partition (GiB):"))
        self.spin_swap_part_gib = Gtk.SpinButton.new_with_range(1, 128, 1)
        self.spin_swap_part_gib.set_value(self.swap_partition_gib)
        self.spin_swap_part_gib.connect("value-changed", self._on_swap_gib_changed)
        self.row_swap_size.append(self.spin_swap_part_gib)
        layout_box.append(self.row_swap_size)
        self.subvol_frame = Gtk.Frame(label="Btrfs-Subvolumes")
        self.subvol_frame.add_css_class("card")
        self.auto_options_box.append(self.subvol_frame)
        subvol_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        subvol_box.set_margin_top(8)
        subvol_box.set_margin_bottom(8)
        subvol_box.set_margin_start(12)
        subvol_box.set_margin_end(12)
        self.subvol_frame.set_child(subvol_box)
        self.subvol_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        subvol_box.append(self.subvol_list_box)
        self._load_disks()
        self._build_subvols_ui()
        self._update_mode_visibility()
        self._update_fs_options_visibility()
        self._update_home_controls()
        self._update_swap_controls()

    def _run_lsblk(self) -> Optional[List[Dict]]:
        try:
            out = subprocess.check_output(
                ["lsblk", "-p", "-J", "-o", "NAME,SIZE,FSTYPE,TYPE,PATH,MOUNTPOINT"],
                text=True,
            )
            return json.loads(out).get("blockdevices", [])
        except Exception as e:
            print(f"Fehler bei lsblk: {e}")
            return None

    def _load_disks(self):
        self.device_combo.remove_all()
        self.disks.clear()
        devices = self._run_lsblk()
        if not devices:
            return
        for dev_info in devices:
            if dev_info.get("type") == "disk":
                self.disks.append(dev_info)
                self.device_combo.append_text(
                    f"{dev_info['path']} ({dev_info['size']})"
                )
        if self.disks:
            self.device_combo.set_active(0)

    def _on_device_changed(self, combo):
        active_text = combo.get_active_text()
        self.selected_disk = active_text.split(" ")[0] if active_text else None

    def _on_mode_changed(self, radio_button):
        if not radio_button.get_active():
            return
        if self.rb_erase.get_active():
            self.mode = "erase"
        self._update_mode_visibility()

    def _on_fs_changed(self, combo):
        self.fs_choice = combo.get_active_text() or "ext4"
        self._update_fs_options_visibility()

    def _on_home_toggled(self, checkbox):
        self.use_separate_home = checkbox.get_active()
        self._update_home_controls()

    def _on_swap_part_toggled(self, checkbox):
        self.use_swap_partition = checkbox.get_active()
        self._update_swap_controls()

    def _on_home_percent_changed(self, spin):
        self.home_size_percent = int(spin.get_value())

    def _on_swap_gib_changed(self, spin):
        self.swap_partition_gib = int(spin.get_value())

    def _update_mode_visibility(self):
        self.auto_options_box.set_visible(True)

    def _update_fs_options_visibility(self):
        is_btrfs = self.fs_choice == "btrfs"
        self.subvol_frame.set_visible(is_btrfs)
        self.home_options_box.set_visible(not is_btrfs)
        if is_btrfs:
            self.cb_home.set_active(True)

    def _update_home_controls(self):
        self.spin_home_percent.set_sensitive(self.use_separate_home)

    def _update_swap_controls(self):
        self.row_swap_size.set_visible(self.use_swap_partition)

    def _build_subvols_ui(self):
        self.subvol_rows.clear()
        child = self.subvol_list_box.get_first_child()
        while child:
            self.subvol_list_box.remove(child)
            child = self.subvol_list_box.get_first_child()
        for name, mnt, checked in BTRFS_DEFAULT_SUBVOLS:
            cb = Gtk.CheckButton.new_with_label(f"{name}  →  {mnt}")
            cb.set_active(checked)
            self.subvol_list_box.append(cb)
            self.subvol_rows.append((name, mnt, cb))

    def get_plan(self) -> Dict[str, Any]:
        plan = {"device": self.selected_disk, "mode": "erase", "uefi": self.is_uefi}
        plan["auto_layout"] = {
            "filesystem": self.fs_choice,
            "use_separate_home": (
                self.use_separate_home if self.fs_choice != "btrfs" else False
            ),
            "home_size_percent": self.home_size_percent,
            "use_swap_partition": self.use_swap_partition,
            "swap_partition_gib": self.swap_partition_gib,
            "esp_size_mib": self.esp_size_mib,
        }
        if self.fs_choice == "btrfs":
            plan["auto_layout"]["subvolumes"] = [
                name for name, _, cb in self.subvol_rows if cb.get_active()
            ]
        return plan

    def validate_plan(self):
        if not self.selected_disk:
            raise ValueError("Kein Ziel-Datenträger ausgewählt.")
