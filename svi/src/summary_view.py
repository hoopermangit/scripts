import gi

gi.require_version("Gtk", "4.0")
from typing import Any, Dict

from gi.repository import Gtk


class SummaryView(Gtk.Box):
    # This page shows a summary of the selected changes

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for s in (
            self.set_margin_top,
            self.set_margin_bottom,
            self.set_margin_start,
            self.set_margin_end,
        ):
            s(6)

        title = Gtk.Label.new("Zusammenfassung")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        self.append(title)

        sc = Gtk.ScrolledWindow()
        sc.set_vexpand(True)
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.append(sc)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        sc.set_child(self.listbox)

        hint = Gtk.Label.new(
            "Bitte prüfe die Angaben – klicke danach auf „Installieren“. "
        )
        hint.set_wrap(True)
        hint.set_halign(Gtk.Align.START)
        self.append(hint)

    def _clear(self):
        rows = []
        child = self.listbox.get_first_child()
        while child:
            rows.append(child)
            child = child.get_next_sibling()
        for r in rows:
            self.listbox.remove(r)

    def update_summary_data(self, data: Dict[str, Any]):
        self._clear()
        if not data:
            self._add_row("Hinweis", "Keine Daten vorhanden.")
            return

        for key, val in data.items():
            text = self._value_to_text(val)
            self._add_row(str(key), text)

    def _value_to_text(self, v: Any) -> str:
        if v is None:
            return "—"
        if isinstance(v, (list, tuple)):
            return ", ".join(map(str, v)) if v else "—"
        if isinstance(v, dict):
            items = []
            for k, val in v.items():
                items.append(f"{k}: {val}")
            return "; ".join(items) if items else "—"
        return str(v)

    def _add_row(self, key: str, value: str):
        row = Gtk.ListBoxRow()
        h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        h.set_margin_top(6)
        h.set_margin_bottom(6)
        h.set_margin_start(6)
        h.set_margin_end(6)

        l_key = Gtk.Label.new(f"{key}:")
        l_key.set_xalign(0)
        l_key.add_css_class("heading")
        l_key.set_hexpand(True)

        l_val = Gtk.Label.new(value)
        l_val.set_xalign(0)
        l_val.set_wrap(True)
        l_val.set_selectable(True)

        h.append(l_key)
        h.append(l_val)
        row.set_child(h)
        self.listbox.append(row)
