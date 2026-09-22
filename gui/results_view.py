from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk

from gui.process_table import apply_table_theme

HEADINGS = ("PID", "AT", "BT", "Priority", "CT", "TAT", "WT", "RT")

# Row colors matching neutral dark palette
_ROW_EVEN = "#17171A"
_ROW_ODD  = "#1E1E22"


def create_results_table(parent: tk.Widget) -> ttk.Treeview:
    apply_table_theme(parent)
    table = ttk.Treeview(
        parent, columns=HEADINGS, show="headings", height=8,
        style="Schedulix.Treeview",
    )
    for heading in HEADINGS:
        table.heading(heading, text=heading)
        table.column(heading, width=78, anchor="center")

    table.tag_configure("even", background=_ROW_EVEN)
    table.tag_configure("odd", background=_ROW_ODD)

    return table
