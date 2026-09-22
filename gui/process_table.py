from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk


HEADINGS = ("PID", "AT", "BT", "Priority")

# ── Schedulix table palette ──────────────────────────────────────────
_BG_DEEP      = "#0D1117"
_BG_SURFACE   = "#161B22"
_BG_CARD      = "#1C2333"
_BORDER       = "#30363D"
_ACCENT       = "#6366F1"
_TEXT_PRIMARY  = "#F0F6FC"
_TEXT_SECONDARY = "#8B949E"
_ROW_EVEN     = "#161B22"
_ROW_ODD      = "#1C2333"
_ROW_SELECT   = "#6366F1"


def apply_table_theme(parent: tk.Widget) -> None:
    """Apply the Schedulix dark theme to all ttk.Treeview widgets."""
    style = ttk.Style(parent)
    style.theme_use("clam")

    style.configure(
        "Schedulix.Treeview",
        background=_BG_SURFACE,
        foreground=_TEXT_PRIMARY,
        fieldbackground=_BG_SURFACE,
        bordercolor=_BORDER,
        borderwidth=1,
        rowheight=28,
        font=("Inter", 11),
    )
    style.configure(
        "Schedulix.Treeview.Heading",
        background=_BG_CARD,
        foreground=_TEXT_SECONDARY,
        bordercolor=_BORDER,
        borderwidth=1,
        font=("Inter", 11, "bold"),
        relief="flat",
    )
    style.map(
        "Schedulix.Treeview",
        background=[("selected", _ROW_SELECT)],
        foreground=[("selected", _TEXT_PRIMARY)],
    )
    style.map(
        "Schedulix.Treeview.Heading",
        background=[("active", _BORDER)],
    )


def create_process_table(parent: tk.Widget) -> ttk.Treeview:
    apply_table_theme(parent)
    table = ttk.Treeview(
        parent, columns=HEADINGS, show="headings", height=7,
        style="Schedulix.Treeview",
    )
    for heading in HEADINGS:
        table.heading(heading, text=heading)
        table.column(heading, width=100, anchor="center")

    table.tag_configure("even", background=_ROW_EVEN)
    table.tag_configure("odd", background=_ROW_ODD)

    return table
