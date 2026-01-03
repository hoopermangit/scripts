#!/usr/bin/env python3
import sys
import os
import gi
import translations
from translations import T

try:
    gi.require_version("Gtk", "4.0")
    gi.require_version("Gdk", "4.0")
    try:
        gi.require_version("Adw", "1")
        from gi.repository import Adw
        USE_ADW = True
    except:
        USE_ADW = False
except ValueError:
    sys.exit(1)

from gi.repository import Gtk, Gdk, Gio

# Views importieren
from welcome_view import WelcomeView
from system_config_view import SystemConfigView
from user_config_view import UserConfigView
from partitioning_view import PartitioningView
from summary_view import SummaryView
from installation_view import InstallationView
from completion_view import CompletionView

BaseApp = Adw.Application if USE_ADW else Gtk.Application

class InstallerApp(BaseApp):
    def __init__(self):
        super().__init__(application_id="org.voidlinux.simpleinstaller", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window = None
        self.stack = None
        self.current_plan = {}
        
    def do_activate(self):
        if not self.window:
            self._load_css()
            if USE_ADW: self.window = Adw.ApplicationWindow(application=self)
            else: self.window = Gtk.ApplicationWindow(application=self)
            
            self.window.set_title("Void Community Installer")
            self.window.set_default_size(950, 650)
            
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            
            # --- Sprachauswahl ---
            # Wir bauen eine ComboBox für die Sprache
            lang_store = Gtk.ListStore(str, str) # ID, Label
            lang_store.append(["en", "🇬🇧 English"])
            lang_store.append(["de", "🇩🇪 Deutsch"])
            lang_store.append(["es", "🇪🇸 Español"])
            lang_store.append(["fr", "🇫🇷 Français"])
            
            self.cmb_lang = Gtk.ComboBox(model=lang_store)
            renderer = Gtk.CellRendererText()
            self.cmb_lang.pack_start(renderer, True)
            self.cmb_lang.add_attribute(renderer, "text", 1)
            self.cmb_lang.set_active_id("en") # Default in UI logic
            # Setze aktive ID basierend auf translations.py
            for row in lang_store:
                if row[0] == translations.CURRENT_LANG:
                    self.cmb_lang.set_active_iter(row.iter)
                    break
            self.cmb_lang.connect("changed", self._on_lang_changed)

            # Header
            if USE_ADW:
                header = Adw.HeaderBar()
                self.lbl_step = Gtk.Label(label=T("step_welcome"), css_classes=["title"])
                header.set_title_widget(self.lbl_step)
                
                self.btn_back = Gtk.Button(label=T("btn_back"))
                self.btn_back.connect("clicked", self._on_back)
                self.btn_back.set_sensitive(False)
                header.pack_start(self.btn_back)
                
                # Sprache links hinzufügen
                header.pack_start(self.cmb_lang)
                
                self.btn_next = Gtk.Button(label=T("btn_next"), css_classes=["suggested-action"])
                self.btn_next.connect("clicked", self._on_next)
                header.pack_end(self.btn_next)
                
                content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                content.append(header)
                content.append(main_box)
                self.window.set_content(content)
            else:
                self.window.set_child(main_box)
                hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, css_classes=["header-bar"])
                hb.set_margin_top(5); hb.set_margin_bottom(5); hb.set_margin_start(10); hb.set_margin_end(10)
                
                self.lbl_step = Gtk.Label(label=T("step_welcome"), css_classes=["title-3"])
                hb.append(self.lbl_step)
                
                hb.append(Gtk.Box(hexpand=True))
                
                # Sprache
                hb.append(self.cmb_lang)
                
                self.btn_back = Gtk.Button(label=T("btn_back"))
                self.btn_back.connect("clicked", self._on_back)
                hb.append(self.btn_back)
                
                self.btn_next = Gtk.Button(label=T("btn_next"), css_classes=["suggested-action"])
                self.btn_next.connect("clicked", self._on_next)
                hb.append(self.btn_next)
                main_box.append(hb)

            # Stack
            self.stack = Gtk.Stack()
            self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
            self.stack.set_vexpand(True)
            main_box.append(self.stack)
            
            self._init_views()
            self.stack.connect("notify::visible-child-name", self._on_page)
            
        self.window.present()

    def _init_views(self):
        # Hilfsmethode um Views (neu) zu laden
        # Alte löschen falls vorhanden (bei Sprachwechsel)
        while self.stack.get_pages().get_n_items() > 0:
            child = self.stack.get_pages().get_item(0).get_child()
            self.stack.remove(child)

        self.view_welcome = WelcomeView()
        self.view_system = SystemConfigView()
        self.view_user = UserConfigView()
        self.view_part = PartitioningView()
        self.view_summary = SummaryView()
        self.view_install = InstallationView()
        self.view_install.set_completion_callback(self._on_done)
        self.view_done = CompletionView(self._reboot, self._quit)
        
        self.stack.add_named(self.view_welcome, "welcome")
        self.stack.add_named(self.view_system, "system")
        self.stack.add_named(self.view_user, "user")
        self.stack.add_named(self.view_part, "part")
        self.stack.add_named(self.view_summary, "summary")
        self.stack.add_named(self.view_install, "install")
        self.stack.add_named(self.view_done, "done")

    def _on_lang_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter:
            model = combo.get_model()
            lang_code = model[tree_iter][0]
            if lang_code != translations.CURRENT_LANG:
                print(f"Switching language to {lang_code}")
                translations.set_language(lang_code)
                
                # UI Refresh Hack: Wir merken uns die aktuelle Seite, laden alle Views neu und gehen zurück
                curr = self.stack.get_visible_child_name() or "welcome"
                self._init_views()
                self.stack.set_visible_child_name(curr)
                
                # Buttons aktualisieren
                self.btn_back.set_label(T("btn_back"))
                # Next label hängt vom Kontext ab, wird in _on_page gesetzt
                self._on_page(self.stack, None)

    def _load_css(self):
        p = Gtk.CssProvider()
        f = os.path.join(os.path.dirname(__file__), "ui.css")
        if os.path.exists(f): p.load_from_path(f)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), p, 1)

    def _on_page(self, s, _):
        n = s.get_visible_child_name()
        # Titel aktualisieren
        t_map = {
            "welcome": "step_welcome", "system": "step_system", "user": "step_user", 
            "part": "step_part", "summary": "step_summary", "install": "step_install", "done": "step_done"
        }
        key = t_map.get(n, "step_welcome")
        self.lbl_step.set_label(T(key))
        
        # Buttons
        self.btn_back.set_sensitive(n not in ["welcome", "install", "done"])
        self.btn_back.set_visible(n != "done")
        self.btn_next.set_visible(n != "done")
        self.btn_next.set_sensitive(n != "install")
        
        if n == "summary":
            self.btn_next.set_label(T("btn_install"))
            self.btn_next.add_css_class("destructive-action")
        else:
            self.btn_next.set_label(T("btn_next"))
            self.btn_next.remove_css_class("destructive-action")

    def _on_back(self, _):
        pages = ["welcome", "system", "user", "part", "summary", "install", "done"]
        c = self.stack.get_visible_child_name()
        if c in pages:
            i = pages.index(c)
            if i > 0: self.stack.set_visible_child_name(pages[i-1])

    def _on_next(self, _):
        c = self.stack.get_visible_child_name()
        try:
            if c == "user": self.view_user.validate_user_input()
            elif c == "part": self.view_part.validate_plan()
        except Exception as e:
            self._err(str(e))
            return

        if c == "summary":
            self._confirm()
        elif c == "part":
            self._collect()
            self.view_summary.update_summary_data(self.current_plan)
            self.stack.set_visible_child_name("summary")
        else:
            pages = ["welcome", "system", "user", "part", "summary", "install", "done"]
            i = pages.index(c)
            if i < len(pages)-1: self.stack.set_visible_child_name(pages[i+1])

    def _collect(self):
        self.current_plan = {
            **self.view_part.get_plan(),
            "language": self.view_system.get_selected_language(),
            "timezone": self.view_system.get_selected_timezone(),
            "keyboard": self.view_system.get_selected_keyboard_layout(),
            "user": self.view_user.get_user_payload(),
            "software": []
        }

    def _confirm(self):
        dlg = Gtk.MessageDialog(transient_for=self.window, modal=True, message_type=Gtk.MessageType.WARNING,
                                buttons=Gtk.ButtonsType.OK_CANCEL, text=T("modal_title"),
                                secondary_text=T("modal_txt"))
        dlg.connect("response", lambda d,r: (d.destroy(), self._start() if r == Gtk.ResponseType.OK else None))
        dlg.present()

    def _start(self):
        self.stack.set_visible_child_name("install")
        self.view_install.set_plan(self.current_plan)
        self.view_install.start_installation()

    def _on_done(self, ok):
        if ok: self.stack.set_visible_child_name("done")
        else: 
            self._err(T("inst_fail"))
            self.btn_back.set_sensitive(True)

    def _err(self, m):
        d = Gtk.MessageDialog(transient_for=self.window, modal=True, message_type=Gtk.MessageType.ERROR,
                              buttons=Gtk.ButtonsType.OK, text=T("err_title"), secondary_text=m)
        d.connect("response", lambda d,r: d.destroy())
        d.present()

    def _reboot(self, _): subprocess.run(["reboot"])
    def _quit(self, _): self.quit()

if __name__ == "__main__":
    if os.geteuid() != 0: sys.exit(1)
    app = InstallerApp()
    app.run(sys.argv)