import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from translations import T

class SummaryView(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.set_margin_top(20)
        self.set_margin_start(20)
        self.set_margin_end(20)
        
        # Titel (Übersetzt)
        self.append(Gtk.Label(label=T("sum_title"), css_classes=["title-2"], xalign=0))
        
        # Liste
        self.lb = Gtk.ListBox(css_classes=["boxed-list"], selection_mode=Gtk.SelectionMode.NONE)
        self.append(self.lb)

    def update_summary_data(self, p):
        # Alte Einträge entfernen
        while self.lb.get_first_child(): 
            self.lb.remove(self.lb.get_first_child())
        
        # Werte für Anzeige aufbereiten
        if p["mode"] == "erase":
            mode_text = T("part_erase")
        else:
            mode_text = T("part_free")
            
        if p.get("use_home"):
            home_text = f"{p['home_size']} GB"
        else:
            home_text = "Root (/)"
        
        # Liste der anzuzeigenden Daten
        # "Software" wurde hier entfernt
        d = [
            (T("sum_dev"), p["device"]),       # Zielfestplatte
            (T("sum_fs"), p["filesystem"]),    # Dateisystem
            (T("sum_mode"), mode_text),        # Modus
            (T("part_home"), home_text),       # Home Partition
            (T("sum_host"), p["user"]["hostname"]), # Hostname
            (T("sum_user"), p["user"]["name"]),     # Benutzer
        ]
        
        # Zeilen erstellen
        for k, v in d:
            r = Gtk.ListBoxRow()
            b = Gtk.Box(spacing=10, margin_top=10, margin_bottom=10, margin_start=10, margin_end=10)
            
            # Label (Fett)
            key_lbl = Gtk.Label(label=f"<b>{k}:</b>", use_markup=True, xalign=0)
            key_lbl.set_size_request(180, -1) # Feste Breite für Ausrichtung
            b.append(key_lbl)
            
            # Wert
            val_lbl = Gtk.Label(label=str(v), xalign=0, wrap=True)
            b.append(val_lbl)
            
            r.set_child(b)
            self.lb.append(r)