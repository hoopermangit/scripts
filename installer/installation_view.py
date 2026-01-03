import gi
import threading
import time

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

# Wichtig: Der Import muss funktionieren. 
# Stelle sicher, dass installation_backend.py im selben Ordner liegt.
from installation_backend import InstallationBackend

class InstallationView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.set_margin_top(20)
        self.set_margin_start(20)
        self.set_margin_end(20)
        
        # Titel
        self.append(Gtk.Label(label="Installation läuft...", css_classes=["title-2"], xalign=0))
        
        # Progress Bar
        self.bar = Gtk.ProgressBar()
        self.bar.set_show_text(True)
        self.append(self.bar)
        
        # Log Bereich
        exp = Gtk.Expander(label="Details / Protokoll")
        self.append(exp)
        
        sc = Gtk.ScrolledWindow()
        sc.set_min_content_height(200)
        sc.set_vexpand(True)
        
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_monospace(True)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        
        sc.set_child(self.log_view)
        exp.set_child(sc)
        
        # Logik
        self.backend = InstallationBackend(log_callback=self._log)
        self.plan = {}
        self.completion_cb = None

    def set_plan(self, plan):
        self.plan = plan

    def set_completion_callback(self, callback):
        self.completion_cb = callback

    def start_installation(self):
        # Starte den Prozess in einem separaten Thread, damit die GUI nicht einfriert
        t = threading.Thread(target=self._run_process, daemon=True)
        t.start()

    def _run_process(self):
        try:
            # 1. Partitionierung
            GLib.idle_add(self._update_ui, 0.1, "Partitionierung...")
            parts = self.backend.apply_partitioning(self.plan)
            # Wir speichern das Ergebnis für den nächsten Schritt
            self.plan["manual_partitions"] = parts 
            
            # 2. Mounten
            GLib.idle_add(self._update_ui, 0.2, "Dateisysteme einhängen...")
            self.backend._mount_filesystems(self.plan)
            
            # 3. Kopieren
            GLib.idle_add(self._update_ui, 0.3, "Kopiere Live-System (das dauert)...")
            self.backend._copy_live_filesystem()
            
            # 4. Konfiguration
            GLib.idle_add(self._update_ui, 0.7, "Konfiguriere System...")
            self.backend._generate_fstab(self.plan)
            self.backend._configure_basics(self.plan)
            self.backend._configure_user(self.plan)
            
            # 5. Finalisieren
            GLib.idle_add(self._update_ui, 0.8, "Erstelle Initramfs...")
            self.backend._finalize()
            
            # 6. Bootloader
            GLib.idle_add(self._update_ui, 0.9, "Installiere Bootloader...")
            self.backend._bootloader(self.plan)
            
            # Fertig
            GLib.idle_add(self._update_ui, 1.0, "Installation abgeschlossen!")
            self.backend._log("--- FERTIG ---")
            
            if self.completion_cb:
                GLib.idle_add(self.completion_cb, True)
                
        except Exception as e:
            # Fehlerbehandlung
            self.backend._log(f"KRITISCHER FEHLER: {e}")
            import traceback
            self.backend._log(traceback.format_exc())
            
            GLib.idle_add(self._update_ui, 0.0, "Fehler aufgetreten!")
            
            if self.completion_cb:
                GLib.idle_add(self.completion_cb, False)
        finally:
            # Aufräumen (Unmount chroot binds)
            self.backend._leave_chroot()

    def _update_ui(self, fraction, text):
        self.bar.set_fraction(fraction)
        self.bar.set_text(text)

    def _log(self, msg):
        def _append():
            buf = self.log_view.get_buffer()
            iter_end = buf.get_end_iter()
            buf.insert(iter_end, str(msg) + "\n")
            # Auto-Scroll
            mark = buf.create_mark(None, buf.get_end_iter(), False)
            self.log_view.scroll_mark_onscreen(mark)
        GLib.idle_add(_append)