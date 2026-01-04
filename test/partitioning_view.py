import gi
import json
import subprocess
import os
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from translations import T

class PartitioningView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.set_margin_top(20)
        self.set_margin_start(20)
        self.set_margin_end(20)
        
        self.selected_disk = None
        self.is_uefi = os.path.exists("/sys/firmware/efi")
        
        # Titel
        title = Gtk.Label(label=T("part_title"))
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        self.append(title)
        
        # Disk Auswahl
        self.append(Gtk.Label(label=T("part_disk"), xalign=0))
        self.combo_disk = Gtk.ComboBoxText()
        self.combo_disk.connect("changed", self._on_disk)
        self.append(self.combo_disk)
        
        # Methoden (Radio Buttons in Cards)
        self.grp = None
        
        # 1. Löschen (Erase)
        self.card_erase = self._make_card(
            T("part_erase"), 
            T("part_erase_desc"), 
            "erase"
        )
        self.append(self.card_erase)
        
        # 2. Freier Speicher (Free Space / Dual Boot)
        self.card_free = self._make_card(
            T("part_free"), 
            T("part_free_desc"), 
            "freespace"
        )
        self.append(self.card_free)
        
        # Opciones Avanzadas
        exp = Gtk.Expander(label="Opciones Avanzadas")
        self.append(exp)
        
        box_opts = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box_opts.set_margin_start(10)
        box_opts.set_margin_top(10)
        exp.set_child(box_opts)
        
        # FS
        box_fs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box_fs.append(Gtk.Label(label=T("part_fs")))
        self.combo_fs = Gtk.ComboBoxText()
        for f in ["ext4", "btrfs", "xfs"]: self.combo_fs.append_text(f)
        self.combo_fs.set_active(0)
        box_fs.append(self.combo_fs)
        box_opts.append(box_fs)
        
        # Swap
        self.chk_swap = Gtk.CheckButton(label=T("part_swap"))
        self.chk_swap.set_active(True)
        box_opts.append(self.chk_swap)
        
        # Home
        self.chk_home = Gtk.CheckButton(label=T("part_home"))
        self.chk_home.connect("toggled", self._on_home)
        box_opts.append(self.chk_home)
        
        self.box_home_size = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.box_home_size.set_sensitive(False)
        self.box_home_size.append(Gtk.Label(label="Tamaño (GB):"))
        self.spin_home = Gtk.SpinButton.new_with_range(10, 9999, 1)
        self.spin_home.set_value(50)
        self.box_home_size.append(self.spin_home)
        box_opts.append(self.box_home_size)
        
        # Disks laden
        self._refresh_disks()

    def _make_card(self, title, desc, mode_id):
        f = Gtk.Frame()
        f.add_css_class("card")
        b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        b.set_margin_top(10); b.set_margin_bottom(10); b.set_margin_start(10)
        f.set_child(b)
        
        rb = Gtk.CheckButton(label=None)
        if not self.grp: 
            self.grp = rb
            rb.set_active(True)
        else:
            rb.set_group(self.grp)
        
        # ID speichern (Widget Name nutzen wir als ID speicher)
        rb.set_name(mode_id)
        
        vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        l1 = Gtk.Label(label=title, xalign=0)
        l1.add_css_class("title-4")
        l2 = Gtk.Label(label=desc, xalign=0, wrap=True)
        l2.add_css_class("dim-label")
        vb.append(l1)
        vb.append(l2)
        
        b.append(rb)
        b.append(vb)
        return f

    def _refresh_disks(self):
        self.combo_disk.remove_all()
        try:
            out = subprocess.check_output(["lsblk", "-d", "-n", "-o", "NAME,SIZE,MODEL", "-p", "-J"])
            data = json.loads(out)
            
            disks = data.get("blockdevices", [])
            # Filter Loop Devices oder zram
            disks = [d for d in disks if not d["name"].startswith("/dev/loop") and not d["name"].startswith("/dev/zram")]
            
            for d in disks:
                model = d.get('model', '') or 'Unbekannt'
                label = f"{d['name']} ({d['size']}) - {model}"
                self.combo_disk.append_text(label)
                
            if disks:
                self.combo_disk.set_active(0)
        except Exception as e:
            print(f"Disk Scan Error: {e}")
            self.combo_disk.append_text("Error al cargar los discos duros.")

    def _on_disk(self, c):
        t = c.get_active_text()
        if t: self.selected_disk = t.split()[0]

    def _on_home(self, b):
        self.box_home_size.set_sensitive(b.get_active())

    def validate_plan(self):
        if not self.selected_disk:
            raise ValueError("Seleccione un disco duro:")

    def get_plan(self):
        # Modus ermitteln
        mode = "erase"
        if self.grp.get_active():
            mode = "erase"
        else:
            mode = "freespace"

        # WICHTIG: Flache Struktur zurückgeben, wie vom Backend erwartet
        return {
            "device": self.selected_disk,
            "mode": mode,
            "uefi": self.is_uefi,
            "filesystem": self.combo_fs.get_active_text(),
            "use_swap": self.chk_swap.get_active(),
            "use_home": self.chk_home.get_active(),
            "home_size": int(self.spin_home.get_value())
        }
