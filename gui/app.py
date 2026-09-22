from __future__ import annotations

import webbrowser
from tkinter import filedialog, messagebox
import customtkinter as ctk

from core.data_io import export_workload, get_sample_workload, import_workload
from core.simulator import SimulationResult, simulate
from gui.comparison_chart import draw_comparison_chart
from gui.gantt_chart import draw_gantt
from gui.results_view import create_results_table
from models.process import Process

# ── Pixel-Perfect Reference Palette (Permanent Dark Developer Dashboard) ──
COLOR_BG_DEEP       = "#121214"  # Deepest window canvas background (neutral dark charcoal)
COLOR_PANEL         = "#17171A"  # Large panel containers (subtle dark gray)
COLOR_CARD          = "#1E1E22"  # Inactive card surface
COLOR_CARD_BORDER   = "#2C2D35"  # Subtle card borders
COLOR_CARD_ACTIVE   = "#FFFFFF"  # Active selected card (pure white as in reference image)
COLOR_TEXT_DARK     = "#121214"  # Dark charcoal text on active white card
COLOR_SUB_DARK      = "#525560"  # Muted slate text on active white card
COLOR_INPUT_BG      = "#141417"  # Form entry background
COLOR_INPUT_BORDER  = "#2E2F38"  # Entry border
COLOR_BTN_GRAY      = "#949494"  # Add Process button surface (light neutral silver/slate)
COLOR_BTN_GRAY_HOV  = "#A8A8A8"  # Add Process button hover
COLOR_BTN_GRAY_TXT  = "#121214"  # Dark bold text for "+ Add Process" button
COLOR_BTN_BAR       = "#212126"  # Toolbar button background (Load Sample, Export, etc.)
COLOR_BTN_BAR_BOR   = "#33343F"  # Toolbar button border
COLOR_BTN_BAR_HOV   = "#2B2C35"  # Toolbar button hover
COLOR_NAV_PILL_ACT  = "#2A2A30"  # Top nav active pill background
COLOR_ACCENT_BLUE   = "#6366F1"  # "Configurable" badge & primary action
COLOR_SUCCESS_GREEN = "#15803D"  # "Simple" badge (emerald forest green)
COLOR_AMBER_BADGE   = "#D97706"  # "Medium" badge (amber/ochre)
COLOR_DANGER_RED    = "#EF4444"  # Delete action trash icon / clear
COLOR_TEXT_WHITE    = "#FFFFFF"  # High contrast primary text
COLOR_TEXT_MUTED    = "#8A909D"  # Secondary text & headings
COLOR_TEXT_LABEL    = "#94A3B8"  # Table column headings
COLOR_DIVIDER       = "#23232A"  # Subtle hairline separator

FONT_FAMILY = "Segoe UI"


class SchedulerApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Schedulix")
        self.geometry("1360x890")
        self.minsize(1120, 760)
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COLOR_BG_DEEP)

        # Workload matching reference image exactly (P1: 0,5,2; P2: 1,3,1; P3: 2,8,3; P4: 3,6,1)
        self.processes: list[Process] = get_sample_workload()
        self.editing_index: int | None = None
        self.selected_algo = ctk.StringVar(value="FCFS")
        self.sjf_mode = ctk.StringVar(value="Non-preemptive (SJF)")
        self.priority_mode = ctk.StringVar(value="Non-preemptive")
        self.quantum_str = ctk.StringVar(value="2")
        self.current_nav = "single"  # "single" or "comparison"

        # Chart widgets
        self.single_chart_canvas = None
        self.comp_bar_canvas = None
        self.comp_gantt_canvas = None
        self.last_single_result: SimulationResult | None = None
        self.comp_results: dict[str, SimulationResult] = {}

        self._build_ui()
        self._refresh_process_table()
        self._update_card_visuals()

    # ── Master Layout ──────────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Header Bar
        self._build_header()

        # 2. Top Segmented Navigation (Pill container)
        self._build_nav_bar()

        # 3. Content View Container
        self.view_container = ctk.CTkFrame(self, fg_color=COLOR_BG_DEEP, corner_radius=0)
        self.view_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(6, 16))
        self.view_container.grid_columnconfigure(0, weight=1)
        self.view_container.grid_rowconfigure(0, weight=1)

        # Build views
        self._build_single_view()
        self._build_comparison_view()

        # Initial view display
        self._switch_view("single")

    # ── 1. Top Header ──────────────────────────────────────────────────
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color=COLOR_PANEL, corner_radius=0, height=64)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        # Left branding block
        brand = ctk.CTkFrame(header, fg_color="transparent")
        brand.grid(row=0, column=0, padx=24, pady=12, sticky="w")

        # CPU Circuit Chip Icon box
        chip_box = ctk.CTkFrame(brand, fg_color=COLOR_CARD, width=38, height=38, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        chip_box.pack(side="left", padx=(0, 12))
        chip_box.pack_propagate(False)
        ctk.CTkLabel(chip_box, text="⊞", font=ctk.CTkFont(size=20), text_color=COLOR_TEXT_WHITE).place(relx=0.5, rely=0.5, anchor="center")

        titles = ctk.CTkFrame(brand, fg_color="transparent")
        titles.pack(side="left")

        ctk.CTkLabel(
            titles, text="Schedulix",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(anchor="w")

        ctk.CTkLabel(
            titles, text="Interactive CPU scheduling algorithm visualization",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", pady=(1, 0))

        # Right actions: GitHub, Docs, (?), Moon
        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.grid(row=0, column=1, padx=24, pady=12, sticky="e")

        # GitHub
        ctk.CTkButton(
            actions, text="⎇  GitHub", width=84, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color="transparent", hover_color=COLOR_CARD,
            border_width=0,
            text_color=COLOR_TEXT_WHITE, corner_radius=6,
            command=self._open_github,
        ).pack(side="left", padx=4)

        # Docs
        ctk.CTkButton(
            actions, text="📖 Docs", width=76, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color="transparent", hover_color=COLOR_CARD,
            border_width=0,
            text_color=COLOR_TEXT_WHITE, corner_radius=6,
            command=self._show_docs,
        ).pack(side="left", padx=4)

        # (?)
        ctk.CTkButton(
            actions, text="?", width=32, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            fg_color="transparent", hover_color=COLOR_CARD,
            border_width=0,
            text_color=COLOR_TEXT_WHITE, corner_radius=16,
            command=self._show_about,
        ).pack(side="left", padx=4)

        # Moon icon (Permanent Dark Theme indicator matching reference)
        ctk.CTkLabel(
            actions, text="🌙", font=ctk.CTkFont(size=14),
            text_color=COLOR_TEXT_MUTED, width=32, height=32,
        ).pack(side="left", padx=(2, 0))

        # Subtle divider under header
        ctk.CTkFrame(self, fg_color=COLOR_CARD_BORDER, height=1, corner_radius=0).grid(row=0, column=0, sticky="sew")

    # ── 2. Navigation Bar (Segmented Container) ────────────────────────
    def _build_nav_bar(self) -> None:
        nav_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        nav_wrapper.grid(row=1, column=0, sticky="ew", padx=20, pady=(12, 6))

        pill_container = ctk.CTkFrame(nav_wrapper, fg_color=COLOR_PANEL, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        pill_container.pack(fill="x", ipady=3)
        pill_container.grid_columnconfigure((0, 1), weight=1)

        self.btn_nav_single = ctk.CTkButton(
            pill_container, text="Single Algorithm Simulation", height=34,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=COLOR_NAV_PILL_ACT, hover_color=COLOR_NAV_PILL_ACT,
            text_color=COLOR_TEXT_WHITE, corner_radius=6,
            border_width=0,
            command=lambda: self._switch_view("single"),
        )
        self.btn_nav_single.grid(row=0, column=0, padx=6, pady=4, sticky="ew")

        self.btn_nav_comp = ctk.CTkButton(
            pill_container, text="Algorithm Comparison", height=34,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color="transparent", hover_color=COLOR_CARD,
            text_color=COLOR_TEXT_MUTED, corner_radius=6,
            border_width=0,
            command=lambda: self._switch_view("comparison"),
        )
        self.btn_nav_comp.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

    def _switch_view(self, target: str) -> None:
        self.current_nav = target
        if target == "single":
            self.btn_nav_single.configure(fg_color=COLOR_NAV_PILL_ACT, text_color=COLOR_TEXT_WHITE, font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"))
            self.btn_nav_comp.configure(fg_color="transparent", text_color=COLOR_TEXT_MUTED, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
            self.comp_view.grid_forget()
            self.single_view.grid(row=0, column=0, sticky="nsew")
        else:
            self.btn_nav_comp.configure(fg_color=COLOR_NAV_PILL_ACT, text_color=COLOR_TEXT_WHITE, font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"))
            self.btn_nav_single.configure(fg_color="transparent", text_color=COLOR_TEXT_MUTED, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
            self.single_view.grid_forget()
            self.comp_view.grid(row=0, column=0, sticky="nsew")
            self.run_comparison()

    # ═══════════════════════════════════════════════════════════════════
    # VIEW 1: SINGLE ALGORITHM SIMULATION
    # ═══════════════════════════════════════════════════════════════════
    def _build_single_view(self) -> None:
        self.single_view = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.single_view.grid_columnconfigure(0, weight=0)  # Left cards
        self.single_view.grid_columnconfigure(1, weight=1)  # Right panel
        self.single_view.grid_rowconfigure(0, weight=1)

        # Left Column: Algorithm Selection Cards
        self._build_algo_panel(self.single_view)

        # Right Column: Scrollable Process Management & Simulation
        self.single_scroll = ctk.CTkScrollableFrame(self.single_view, fg_color=COLOR_BG_DEEP, corner_radius=0)
        self.single_scroll.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.single_scroll.grid_columnconfigure(0, weight=1)

        # Process Management Card
        self._build_process_management_card(self.single_scroll)

        # Simulation & Results Card
        self._build_simulation_card(self.single_scroll)

    # ── Left Column: Algorithm Selection Cards ─────────────────────────
    def _build_algo_panel(self, parent: ctk.CTkFrame) -> None:
        panel = ctk.CTkFrame(parent, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER, width=320)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        panel.grid_propagate(False)

        # Header with clock icon
        header_f = ctk.CTkFrame(panel, fg_color="transparent")
        header_f.pack(fill="x", padx=16, pady=(16, 2))
        ctk.CTkLabel(
            header_f, text="🕒  Algorithm Selection",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(anchor="w")

        ctk.CTkLabel(
            panel, text="Choose and configure a scheduling algorithm",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLOR_TEXT_MUTED,
        ).pack(padx=16, pady=(0, 12), anchor="w")

        self.cards_data: dict[str, dict] = {}

        # 1. FCFS
        self._add_card(
            panel, "FCFS", "🕒", "First Come\nFirst Serve",
            [("Configurable", COLOR_ACCENT_BLUE), ("Simple", COLOR_SUCCESS_GREEN)],
            "Processes jobs in order of arrival\n(configurable preemptive)",
        )

        # 2. Round Robin
        self._add_card(
            panel, "Round Robin", "⏱", "Round Robin",
            [("Configurable", COLOR_ACCENT_BLUE), ("Medium", COLOR_AMBER_BADGE)],
            "Fixed time quantum for fair CPU sharing\n(configurable preemptive)",
            config_type="quantum",
        )

        # 3. Shortest Job First
        self._add_card(
            panel, "SJF", "⚡", "Shortest Job\nFirst",
            [("Configurable", COLOR_ACCENT_BLUE), ("Medium", COLOR_AMBER_BADGE)],
            "Selects the shortest job first (configurable\npreemptive)",
            config_type="sjf_mode",
        )

        # 4. Priority Scheduling
        self._add_card(
            panel, "Priority", "👑", "Priority\nScheduling",
            [("Configurable", COLOR_ACCENT_BLUE), ("Medium", COLOR_AMBER_BADGE)],
            "Schedules based on priority, choose min or\nmax as highest",
            config_type="priority_mode",
        )

    def _add_card(
        self, parent: ctk.CTkFrame, algo_id: str, icon_char: str, title: str,
        badges: list[tuple[str, str]], desc: str, config_type: str | None = None,
    ) -> None:
        card = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        card.pack(fill="x", padx=14, pady=5)

        # Top row: icon + title + badges
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 4))

        icon_lbl = ctk.CTkLabel(top_row, text=icon_char, font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_WHITE)
        icon_lbl.pack(side="left", padx=(0, 8), anchor="n")

        title_lbl = ctk.CTkLabel(
            top_row, text=title, justify="left",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        )
        title_lbl.pack(side="left", anchor="n")

        badge_box = ctk.CTkFrame(top_row, fg_color="transparent")
        badge_box.pack(side="right", anchor="n")
        for b_text, b_color in badges:
            b = ctk.CTkLabel(
                badge_box, text=b_text,
                font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
                fg_color=b_color, text_color="#FFFFFF", corner_radius=4, padx=6, pady=2,
            )
            b.pack(side="left", padx=2)

        desc_lbl = ctk.CTkLabel(
            card, text=desc, justify="left",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLOR_TEXT_MUTED,
        )
        desc_lbl.pack(padx=12, pady=(0, 10), anchor="w")

        # Config controls inside card if active
        config_frame = ctk.CTkFrame(card, fg_color="transparent")
        if config_type == "quantum":
            ctk.CTkLabel(config_frame, text="Time Quantum:", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_MUTED).pack(side="left", padx=(0, 6))
            entry_q = ctk.CTkEntry(
                config_frame, textvariable=self.quantum_str, width=64, height=26,
                font=ctk.CTkFont(size=11), fg_color=COLOR_INPUT_BG, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_WHITE,
            )
            entry_q.pack(side="left")
        elif config_type == "sjf_mode":
            seg_sjf = ctk.CTkSegmentedButton(
                config_frame, values=["Non-preemptive (SJF)", "Preemptive (SRTF)"],
                variable=self.sjf_mode, font=ctk.CTkFont(size=10, weight="bold"),
                selected_color=COLOR_ACCENT_BLUE, unselected_color=COLOR_INPUT_BG,
                text_color=COLOR_TEXT_WHITE,
            )
            seg_sjf.pack(fill="x")
        elif config_type == "priority_mode":
            seg_pr = ctk.CTkSegmentedButton(
                config_frame, values=["Non-preemptive", "Preemptive"],
                variable=self.priority_mode, font=ctk.CTkFont(size=10, weight="bold"),
                selected_color=COLOR_ACCENT_BLUE, unselected_color=COLOR_INPUT_BG,
                text_color=COLOR_TEXT_WHITE,
            )
            seg_pr.pack(fill="x")

        # Store widget references for visual switching
        self.cards_data[algo_id] = {
            "frame": card,
            "title_lbl": title_lbl,
            "desc_lbl": desc_lbl,
            "icon_lbl": icon_lbl,
            "config_frame": config_frame,
            "has_config": (config_type is not None),
        }

        # Recursive binding for click
        def bind_click(widget):
            widget.bind("<Button-1>", lambda e, a=algo_id: self._select_algorithm(a))
            for child in widget.winfo_children():
                # Avoid overriding entry fields or segmented button clicks
                if not isinstance(child, (ctk.CTkEntry, ctk.CTkSegmentedButton)):
                    bind_click(child)

        bind_click(card)

    def _select_algorithm(self, algo_id: str) -> None:
        self.selected_algo.set(algo_id)
        self._update_card_visuals()

    def _update_card_visuals(self) -> None:
        chosen = self.selected_algo.get()
        for aid, data in self.cards_data.items():
            card = data["frame"]
            if aid == chosen:
                # Active white card matching reference image
                card.configure(fg_color=COLOR_CARD_ACTIVE, border_color=COLOR_CARD_ACTIVE, border_width=1)
                data["title_lbl"].configure(text_color=COLOR_TEXT_DARK)
                data["desc_lbl"].configure(text_color=COLOR_SUB_DARK)
                data["icon_lbl"].configure(text_color=COLOR_TEXT_DARK)
                if data["has_config"]:
                    data["config_frame"].pack(fill="x", padx=12, pady=(0, 10))
            else:
                # Inactive dark card matching reference image
                card.configure(fg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER, border_width=1)
                data["title_lbl"].configure(text_color=COLOR_TEXT_WHITE)
                data["desc_lbl"].configure(text_color=COLOR_TEXT_MUTED)
                data["icon_lbl"].configure(text_color=COLOR_TEXT_WHITE)
                if data["has_config"]:
                    data["config_frame"].pack_forget()

    # ── Right Column: Process Management Card ──────────────────────────
    def _build_process_management_card(self, parent: ctk.CTkScrollableFrame) -> None:
        card = ctk.CTkFrame(parent, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        card.pack(fill="x", pady=(0, 14))

        # Top Bar: Title on left, Action Toolbar on right
        top_bar = ctk.CTkFrame(card, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(16, 12))

        info_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        info_box.pack(side="left")
        ctk.CTkLabel(
            info_box, text="Process Management",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(anchor="w")
        ctk.CTkLabel(
            info_box, text="Add, edit, or remove processes from the scheduling queue",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 0))

        # Action Toolbar (Load Sample, Export, Import, Clear All)
        toolbar = ctk.CTkFrame(top_bar, fg_color="transparent")
        toolbar.pack(side="right")

        self._toolbar_btn(toolbar, "📄 Load Sample", self._load_sample_workload)
        self._toolbar_btn(toolbar, "📥 Export", self._export_workload_file)
        self._toolbar_btn(toolbar, "📤 Import", self._import_workload_file)
        self._toolbar_btn(toolbar, "✕ Clear All", self._clear_all_processes)

        # ── Add New Process Box ───────────────────────────────────────
        form_box = ctk.CTkFrame(card, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        form_box.pack(fill="x", padx=20, pady=(0, 16))

        self.lbl_form_mode = ctk.CTkLabel(
            form_box, text="Add New Process",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        )
        self.lbl_form_mode.pack(padx=16, pady=(12, 6), anchor="w")

        fields_row = ctk.CTkFrame(form_box, fg_color="transparent")
        fields_row.pack(fill="x", padx=16, pady=(0, 14))
        fields_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.entry_pid = self._form_input(fields_row, 0, "Process ID", "P1")
        self.entry_at = self._form_input(fields_row, 1, "Arrival Time", "0")
        self.entry_bt = self._form_input(fields_row, 2, "Burst Time", "1")
        self.entry_pr = self._form_input(fields_row, 3, "Priority", "1")

        self.btn_submit_process = ctk.CTkButton(
            fields_row, text="+   Add Process", height=36, width=160,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=COLOR_BTN_GRAY, hover_color=COLOR_BTN_GRAY_HOV,
            text_color=COLOR_BTN_GRAY_TXT, corner_radius=6,
            command=self._on_submit_process,
        )
        self.btn_submit_process.grid(row=1, column=4, padx=(12, 0), pady=(0, 2), sticky="s")

        self.btn_cancel_edit = ctk.CTkButton(
            fields_row, text="Cancel", height=36, width=70,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_INPUT_BG, hover_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_MUTED, corner_radius=6,
            command=self._cancel_edit,
        )

        # ── Current Processes (N) Table ───────────────────────────────
        tbl_top = ctk.CTkFrame(card, fg_color="transparent")
        tbl_top.pack(fill="x", padx=20, pady=(4, 6))
        self.lbl_proc_count = ctk.CTkLabel(
            tbl_top, text="Current Processes (4)",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        )
        self.lbl_proc_count.pack(anchor="w")

        # Table Column Headers matching reference
        th = ctk.CTkFrame(card, fg_color="transparent", height=28)
        th.pack(fill="x", padx=20, pady=(2, 4))
        th.grid_columnconfigure(0, weight=2)  # Process ID
        th.grid_columnconfigure(1, weight=2)  # Arrival Time
        th.grid_columnconfigure(2, weight=2)  # Burst Time
        th.grid_columnconfigure(3, weight=2)  # Priority
        th.grid_columnconfigure(4, weight=2)  # Actions

        headers = ["Process ID", "Arrival Time", "Burst Time", "Priority", "Actions"]
        for col, title in enumerate(headers):
            st = "w" if col == 0 else ("e" if col == 4 else "")
            ctk.CTkLabel(
                th, text=title, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                text_color=COLOR_TEXT_LABEL,
            ).grid(row=0, column=col, padx=12, pady=4, sticky=st)

        # Process Rows Container
        self.proc_rows_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.proc_rows_frame.pack(fill="x", padx=20, pady=(0, 16))

    def _form_input(self, parent: ctk.CTkFrame, col: int, label: str, placeholder: str) -> ctk.CTkEntry:
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=0, column=col, rowspan=2, padx=4, sticky="ew")
        ctk.CTkLabel(box, text=label, font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_WHITE).pack(anchor="w", pady=(0, 4))
        entry = ctk.CTkEntry(
            box, height=36, font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_INPUT_BG, border_color=COLOR_INPUT_BORDER, text_color=COLOR_TEXT_WHITE,
            placeholder_text=placeholder, placeholder_text_color="#5E6273",
            corner_radius=6,
        )
        entry.pack(fill="x")
        return entry

    def _toolbar_btn(self, parent: ctk.CTkFrame, text: str, command) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            parent, text=text, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLOR_BTN_BAR, hover_color=COLOR_BTN_BAR_HOV,
            border_width=1, border_color=COLOR_BTN_BAR_BOR,
            text_color=COLOR_TEXT_WHITE, corner_radius=6, command=command,
        )
        btn.pack(side="left", padx=3)
        return btn

    # ── Refresh Table Rows ─────────────────────────────────────────────
    def _refresh_process_table(self) -> None:
        for w in self.proc_rows_frame.winfo_children():
            w.destroy()

        self.lbl_proc_count.configure(text=f"Current Processes ({len(self.processes)})")

        if not self.processes:
            empty = ctk.CTkLabel(
                self.proc_rows_frame,
                text="No processes in queue. Click '+ Add Process' or '📄 Load Sample' to begin.",
                font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MUTED,
            )
            empty.pack(pady=20)
            return

        for idx, p in enumerate(self.processes):
            row = ctk.CTkFrame(self.proc_rows_frame, fg_color="transparent", height=42)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=2)
            row.grid_columnconfigure(1, weight=2)
            row.grid_columnconfigure(2, weight=2)
            row.grid_columnconfigure(3, weight=2)
            row.grid_columnconfigure(4, weight=2)

            # Process ID (bold white)
            ctk.CTkLabel(row, text=p.pid, font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=COLOR_TEXT_WHITE).grid(row=0, column=0, padx=12, sticky="w")
            # Arrival Time
            ctk.CTkLabel(row, text=str(p.arrival_time), font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=COLOR_TEXT_WHITE).grid(row=0, column=1, padx=12)
            # Burst Time
            ctk.CTkLabel(row, text=str(p.burst_time), font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=COLOR_TEXT_WHITE).grid(row=0, column=2, padx=12)
            # Priority
            ctk.CTkLabel(row, text=str(p.priority), font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=COLOR_TEXT_WHITE).grid(row=0, column=3, padx=12)

            # Actions (Edit ✎, Delete 🗑)
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.grid(row=0, column=4, padx=12, sticky="e")

            # Edit button (gray pencil icon)
            btn_edit = ctk.CTkButton(
                act, text="✎", width=32, height=28,
                font=ctk.CTkFont(size=13), fg_color="transparent", hover_color=COLOR_CARD,
                text_color=COLOR_TEXT_MUTED, corner_radius=4,
                command=lambda i=idx: self._start_edit(i),
            )
            btn_edit.pack(side="left", padx=2)

            # Delete button (red trash can icon)
            btn_del = ctk.CTkButton(
                act, text="🗑", width=32, height=28,
                font=ctk.CTkFont(size=13), fg_color="transparent", hover_color="#2A1A1E",
                text_color=COLOR_DANGER_RED, corner_radius=4,
                command=lambda i=idx: self._delete_process(i),
            )
            btn_del.pack(side="left", padx=2)

            # Hairline divider between table rows
            ctk.CTkFrame(self.proc_rows_frame, fg_color=COLOR_DIVIDER, height=1).pack(fill="x", padx=4, pady=(2, 2))

    # ── Process CRUD Handlers ──────────────────────────────────────────
    def _on_submit_process(self) -> None:
        try:
            pid = self.entry_pid.get().strip()
            if not pid:
                raise ValueError("Process ID (PID) cannot be empty.")

            try:
                at = int(self.entry_at.get().strip())
                bt = int(self.entry_bt.get().strip())
                pr = int(self.entry_pr.get().strip())
            except ValueError:
                raise ValueError("Arrival Time, Burst Time, and Priority must be integers.")

            if at < 0:
                raise ValueError("Arrival Time must be non-negative (≥ 0).")
            if bt <= 0:
                raise ValueError("Burst Time must be greater than zero (> 0).")
            if pr <= 0:
                raise ValueError("Priority must be a positive integer (≥ 1). Lower number = higher priority.")

            # Duplicate PID check
            for i, p in enumerate(self.processes):
                if p.pid == pid and (self.editing_index is None or i != self.editing_index):
                    raise ValueError(f"Process ID '{pid}' already exists. Every process must have a unique identifier.")

            if self.editing_index is not None:
                self.processes[self.editing_index] = Process(pid, at, bt, pr, order=self.editing_index)
                self._cancel_edit()
            else:
                self.processes.append(Process(pid, at, bt, pr, order=len(self.processes)))
                self._clear_form()

            self._refresh_process_table()

        except ValueError as err:
            messagebox.showerror("Process Input Error", str(err))

    def _start_edit(self, index: int) -> None:
        self.editing_index = index
        p = self.processes[index]
        self._clear_form()
        self.entry_pid.insert(0, p.pid)
        self.entry_at.insert(0, str(p.arrival_time))
        self.entry_bt.insert(0, str(p.burst_time))
        self.entry_pr.insert(0, str(p.priority))

        self.lbl_form_mode.configure(text=f"Edit Process: {p.pid}")
        self.btn_submit_process.configure(text="✔ Save Edit")
        self.btn_cancel_edit.grid(row=1, column=5, padx=(4, 0), pady=(0, 2), sticky="s")

    def _cancel_edit(self) -> None:
        self.editing_index = None
        self._clear_form()
        self.lbl_form_mode.configure(text="Add New Process")
        self.btn_submit_process.configure(text="+   Add Process")
        self.btn_cancel_edit.grid_forget()

    def _clear_form(self) -> None:
        self.entry_pid.delete(0, "end")
        self.entry_at.delete(0, "end")
        self.entry_bt.delete(0, "end")
        self.entry_pr.delete(0, "end")

    def _delete_process(self, index: int) -> None:
        if self.editing_index == index:
            self._cancel_edit()
        self.processes.pop(index)
        for i, p in enumerate(self.processes):
            p.order = i
        self._refresh_process_table()

    def _clear_all_processes(self) -> None:
        self._cancel_edit()
        self.processes.clear()
        self._refresh_process_table()
        self.reset_single_results()

    def _load_sample_workload(self) -> None:
        self._cancel_edit()
        self.processes = get_sample_workload()
        self._refresh_process_table()

    def _export_workload_file(self) -> None:
        if not self.processes:
            messagebox.showwarning("Export Workload", "There are no processes to export.")
            return
        filepath = filedialog.asksaveasfilename(
            title="Export Workload",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv")],
        )
        if filepath:
            try:
                export_workload(self.processes, filepath)
                messagebox.showinfo("Export Successful", f"Workload successfully exported to:\n{filepath}")
            except Exception as err:
                messagebox.showerror("Export Failed", str(err))

    def _import_workload_file(self) -> None:
        filepath = filedialog.askopenfilename(
            title="Import Workload",
            filetypes=[("Workload Files", "*.json;*.csv"), ("JSON Files", "*.json"), ("CSV Files", "*.csv")],
        )
        if filepath:
            try:
                loaded = import_workload(filepath)
                self._cancel_edit()
                self.processes = loaded
                self._refresh_process_table()
                messagebox.showinfo("Import Successful", f"Successfully imported {len(loaded)} processes from:\n{filepath}")
            except Exception as err:
                messagebox.showerror("Import Failed", str(err))

    # ── Simulation & Results Card ──────────────────────────────────────
    def _build_simulation_card(self, parent: ctk.CTkScrollableFrame) -> None:
        self.sim_card = ctk.CTkFrame(parent, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        self.sim_card.pack(fill="x", pady=(0, 20))

        # Simulation Toolbar
        action_bar = ctk.CTkFrame(self.sim_card, fg_color="transparent")
        action_bar.pack(fill="x", padx=20, pady=16)

        ctk.CTkButton(
            action_bar, text="▶   Run Simulation", height=38, width=170,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=COLOR_ACCENT_BLUE, hover_color="#818CF8", text_color=COLOR_TEXT_WHITE,
            corner_radius=6, command=self.run_single_simulation,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_bar, text="↺  Reset Results", height=38, width=130,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=COLOR_CARD, hover_color=COLOR_CARD_BORDER, border_width=1, border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE, corner_radius=6, command=self.reset_single_results,
        ).pack(side="left")

        # Results Container
        self.results_container = ctk.CTkFrame(self.sim_card, fg_color="transparent")
        self.results_container.pack(fill="x", padx=20, pady=(0, 16))

        self.lbl_sim_empty = ctk.CTkLabel(
            self.results_container, text="Select an algorithm from the left panel and click '▶ Run Simulation' to view the Gantt chart and performance metrics.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MUTED,
        )
        self.lbl_sim_empty.pack(pady=24)

    # ── Run Single Simulation ──────────────────────────────────────────
    def run_single_simulation(self) -> None:
        if not self.processes:
            messagebox.showwarning("Simulation Error", "Please add at least one process before running simulation.")
            return

        algo_choice = self.selected_algo.get()
        try:
            quantum = int(self.quantum_str.get().strip())
            if quantum <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Time Quantum Error", "Time Quantum must be a positive integer (> 0).")
            return

        sim_algo = algo_choice
        is_preemptive = False

        if algo_choice == "SJF":
            sim_algo = "SRTF" if self.sjf_mode.get() == "Preemptive (SRTF)" else "SJF"
        elif algo_choice == "Priority":
            sim_algo = "Priority"
            is_preemptive = (self.priority_mode.get() == "Preemptive")

        try:
            result = simulate(self.processes, sim_algo, quantum=quantum, priority_preemptive=is_preemptive)
            self.last_single_result = result
            self._render_single_results(result, algo_choice)
        except Exception as err:
            messagebox.showerror("Simulation Failure", str(err))

    def _render_single_results(self, result: SimulationResult, algo_choice: str) -> None:
        for w in self.results_container.winfo_children():
            w.destroy()

        # 1. Gantt Chart Section
        ctk.CTkLabel(
            self.results_container, text="Gantt Chart Timeline",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(anchor="w", pady=(4, 8))

        gantt_box = ctk.CTkFrame(self.results_container, fg_color=COLOR_BG_DEEP, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        gantt_box.pack(fill="x", pady=(0, 16))

        if self.single_chart_canvas:
            try:
                self.single_chart_canvas.get_tk_widget().destroy()
            except Exception:
                pass

        algo_label = result.algorithm
        if algo_choice == "Priority":
            algo_label = f"Priority ({'Preemptive' if self.priority_mode.get() == 'Preemptive' else 'Non-preemptive'})"
        elif algo_choice == "Round Robin":
            algo_label = f"Round Robin (Quantum = {self.quantum_str.get()})"

        self.single_chart_canvas = draw_gantt(gantt_box, result.segments, f"Gantt Chart — {algo_label}")
        self.single_chart_canvas.get_tk_widget().pack(fill="x", padx=6, pady=6)

        # 2. Aggregate Metric Cards (Grid of 6)
        ctk.CTkLabel(
            self.results_container, text="Aggregate Performance Metrics",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(anchor="w", pady=(0, 8))

        metrics_grid = ctk.CTkFrame(self.results_container, fg_color="transparent")
        metrics_grid.pack(fill="x", pady=(0, 16))

        s = result.summary
        metrics_data = [
            ("Avg Waiting Time", f"{s.average_waiting_time:.2f} units"),
            ("Avg Turnaround Time", f"{s.average_turnaround_time:.2f} units"),
            ("Avg Response Time", f"{s.average_response_time:.2f} units"),
            ("CPU Utilization", f"{s.cpu_utilization:.1f}%"),
            ("Throughput", f"{s.throughput:.3f} p/u"),
            ("Total Time", f"{s.total_time} units"),
        ]

        for col, (m_title, m_val) in enumerate(metrics_data):
            metrics_grid.grid_columnconfigure(col, weight=1)
            card = ctk.CTkFrame(metrics_grid, fg_color=COLOR_CARD, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
            card.grid(row=0, column=col, padx=4, pady=2, sticky="ew")

            ctk.CTkLabel(
                card, text=m_val,
                font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
                text_color=COLOR_ACCENT_BLUE,
            ).pack(padx=8, pady=(10, 2))

            ctk.CTkLabel(
                card, text=m_title,
                font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                text_color=COLOR_TEXT_MUTED,
            ).pack(padx=8, pady=(0, 10))

        # 3. Process Execution Metrics Table
        ctk.CTkLabel(
            self.results_container, text="Process Execution Details",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(anchor="w", pady=(0, 8))

        res_table_frame = ctk.CTkFrame(self.results_container, fg_color=COLOR_CARD, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        res_table_frame.pack(fill="x")

        table = create_results_table(res_table_frame)
        table.pack(fill="x", padx=10, pady=10)

        for i, p in enumerate(result.processes):
            tag = "even" if i % 2 == 0 else "odd"
            table.insert(
                "", "end",
                values=(
                    p.pid, p.arrival_time, p.burst_time, p.priority,
                    p.completion_time, p.turnaround_time, p.waiting_time, p.response_time,
                ),
                tags=(tag,),
            )

    def reset_single_results(self) -> None:
        self.last_single_result = None
        for w in self.results_container.winfo_children():
            w.destroy()
        self.lbl_sim_empty = ctk.CTkLabel(
            self.results_container, text="Select an algorithm from the left panel and click '▶ Run Simulation' to view the Gantt chart and performance metrics.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MUTED,
        )
        self.lbl_sim_empty.pack(pady=24)

    # ═══════════════════════════════════════════════════════════════════
    # VIEW 2: ALGORITHM COMPARISON
    # ═══════════════════════════════════════════════════════════════════
    def _build_comparison_view(self) -> None:
        self.comp_view = ctk.CTkScrollableFrame(self.view_container, fg_color=COLOR_BG_DEEP, corner_radius=0)
        self.comp_view.grid_columnconfigure(0, weight=1)

    def run_comparison(self) -> None:
        for w in self.comp_view.winfo_children():
            w.destroy()

        if not self.processes:
            empty = ctk.CTkLabel(
                self.comp_view,
                text="No processes available for comparison. Switch back to 'Single Algorithm Simulation' and add processes.",
                font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=COLOR_TEXT_MUTED,
            )
            empty.pack(pady=40)
            return

        try:
            q = int(self.quantum_str.get().strip())
            if q <= 0:
                q = 2
        except ValueError:
            q = 2

        # 6 explicit configurations evaluated on isolated copies
        configs = [
            ("FCFS", "FCFS", q, False),
            ("SJF (Non-preemptive)", "SJF", q, False),
            ("SRTF (Preemptive)", "SRTF", q, False),
            (f"Round Robin (q={q})", "Round Robin", q, False),
            ("Priority (Non-preemptive)", "Priority", q, False),
            ("Priority (Preemptive)", "Priority", q, True),
        ]

        self.comp_results = {}
        for display_name, algo_key, quantum_val, is_preempt in configs:
            self.comp_results[display_name] = simulate(self.processes, algo_key, quantum=quantum_val, priority_preemptive=is_preempt)

        # 1. Header Card
        top_card = ctk.CTkFrame(self.comp_view, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        top_card.pack(fill="x", pady=(0, 14))

        top_row = ctk.CTkFrame(top_card, fg_color="transparent")
        top_row.pack(fill="x", padx=20, pady=16)

        info_b = ctk.CTkFrame(top_row, fg_color="transparent")
        info_b.pack(side="left")
        ctk.CTkLabel(
            info_b, text="Algorithm Comparison",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(anchor="w")
        ctk.CTkLabel(
            info_b, text=f"Evaluating 6 configurations on the same workload ({len(self.processes)} processes) • Round Robin Time Quantum = {q} • Priority Rule: Lower number = Higher priority",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", pady=(3, 0))

        ctk.CTkButton(
            top_row, text="↺  Refresh Comparison", height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_CARD, hover_color=COLOR_CARD_BORDER, border_width=1, border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE, corner_radius=6, command=self.run_comparison,
        ).pack(side="right")

        # 2. Side-by-side Bar Chart
        chart_card = ctk.CTkFrame(self.comp_view, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        chart_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            chart_card, text="Waiting Time & Turnaround Time Comparison",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(padx=20, pady=(14, 4), anchor="w")

        chart_box = ctk.CTkFrame(chart_card, fg_color="transparent")
        chart_box.pack(fill="x", padx=14, pady=(0, 14))

        if self.comp_bar_canvas:
            try:
                self.comp_bar_canvas.get_tk_widget().destroy()
            except Exception:
                pass
        self.comp_bar_canvas = draw_comparison_chart(chart_box, self.comp_results)
        self.comp_bar_canvas.get_tk_widget().pack(fill="x")

        # 3. Comparative Metrics Table Card
        tbl_card = ctk.CTkFrame(self.comp_view, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        tbl_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            tbl_card, text="Comparative Performance Metrics",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(padx=20, pady=(14, 4), anchor="w")

        # Table Header
        th = ctk.CTkFrame(tbl_card, fg_color=COLOR_CARD, height=32, corner_radius=6)
        th.pack(fill="x", padx=20, pady=(4, 4))
        th.grid_columnconfigure(0, weight=3)
        th.grid_columnconfigure((1, 2, 3, 4, 5), weight=2)

        headings = ["Algorithm Configuration", "Avg WT (units)", "Avg TAT (units)", "Avg RT (units)", "Throughput (p/u)", "CPU Util. (%)"]
        for col, title in enumerate(headings):
            st = "w" if col == 0 else ""
            ctk.CTkLabel(
                th, text=title, font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                text_color=COLOR_TEXT_LABEL,
            ).grid(row=0, column=col, padx=10, pady=6, sticky=st)

        # Rows
        for idx, (name, res) in enumerate(self.comp_results.items()):
            row_bg = COLOR_PANEL if idx % 2 == 0 else COLOR_CARD
            row = ctk.CTkFrame(tbl_card, fg_color=row_bg, corner_radius=4, height=34)
            row.pack(fill="x", padx=20, pady=2)
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure((1, 2, 3, 4, 5), weight=2)

            s = res.summary
            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_WHITE).grid(row=0, column=0, padx=12, sticky="w")
            ctk.CTkLabel(row, text=f"{s.average_waiting_time:.2f}", font=ctk.CTkFont(size=12), text_color=COLOR_ACCENT_BLUE).grid(row=0, column=1, padx=8)
            ctk.CTkLabel(row, text=f"{s.average_turnaround_time:.2f}", font=ctk.CTkFont(size=12), text_color=COLOR_SUCCESS_GREEN).grid(row=0, column=2, padx=8)
            ctk.CTkLabel(row, text=f"{s.average_response_time:.2f}", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_WHITE).grid(row=0, column=3, padx=8)
            ctk.CTkLabel(row, text=f"{s.throughput:.3f}", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_WHITE).grid(row=0, column=4, padx=8)
            ctk.CTkLabel(row, text=f"{s.cpu_utilization:.2f}%", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_WHITE).grid(row=0, column=5, padx=8)

        # 4. Workload-Specific Observations
        obs_card = ctk.CTkFrame(self.comp_view, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        obs_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            obs_card, text="Workload-Specific Observations",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(padx=20, pady=(14, 4), anchor="w")

        best_wt_algo = min(self.comp_results.items(), key=lambda item: item[1].summary.average_waiting_time)
        best_tat_algo = min(self.comp_results.items(), key=lambda item: item[1].summary.average_turnaround_time)
        best_rt_algo = min(self.comp_results.items(), key=lambda item: item[1].summary.average_response_time)

        obs_text = (
            f"• Lowest Average Waiting Time on this workload: {best_wt_algo[0]} ({best_wt_algo[1].summary.average_waiting_time:.2f} time units)\n"
            f"• Lowest Average Turnaround Time on this workload: {best_tat_algo[0]} ({best_tat_algo[1].summary.average_turnaround_time:.2f} time units)\n"
            f"• Lowest Average Response Time on this workload: {best_rt_algo[0]} ({best_rt_algo[1].summary.average_response_time:.2f} time units)\n\n"
            "Academic Note: Performance observations are strictly specific to the current workload and configuration. "
            "In operating system scheduling theory, no single algorithm is globally superior across all workloads."
        )

        ctk.CTkLabel(
            obs_card, text=obs_text, justify="left",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MUTED,
        ).pack(padx=20, pady=(0, 16), anchor="w")

        # 5. Gantt Chart Inspector
        insp_card = ctk.CTkFrame(self.comp_view, fg_color=COLOR_PANEL, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        insp_card.pack(fill="x", pady=(0, 20))

        insp_top = ctk.CTkFrame(insp_card, fg_color="transparent")
        insp_top.pack(fill="x", padx=20, pady=(14, 8))

        ctk.CTkLabel(
            insp_top, text="Gantt Chart Inspector",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(side="left")

        self.comp_inspect_choice = ctk.StringVar(value=list(self.comp_results.keys())[0])
        opt = ctk.CTkOptionMenu(
            insp_top, values=list(self.comp_results.keys()),
            variable=self.comp_inspect_choice, width=240, height=30,
            font=ctk.CTkFont(size=12), fg_color=COLOR_CARD, button_color=COLOR_ACCENT_BLUE,
            dropdown_fg_color=COLOR_CARD, text_color=COLOR_TEXT_WHITE,
            command=self._render_comp_gantt,
        )
        opt.pack(side="right")

        self.comp_gantt_box = ctk.CTkFrame(insp_card, fg_color="transparent")
        self.comp_gantt_box.pack(fill="x", padx=14, pady=(0, 14))

        self._render_comp_gantt(self.comp_inspect_choice.get())

    def _render_comp_gantt(self, algo_name: str) -> None:
        for w in self.comp_gantt_box.winfo_children():
            w.destroy()

        if algo_name in self.comp_results:
            res = self.comp_results[algo_name]
            canvas = draw_gantt(self.comp_gantt_box, res.segments, f"Gantt Chart — {algo_name}")
            canvas.get_tk_widget().pack(fill="x")

    # ═══════════════════════════════════════════════════════════════════
    # MODALS: ABOUT & DOCUMENTATION
    # ═══════════════════════════════════════════════════════════════════
    def _open_github(self) -> None:
        webbrowser.open("https://github.com/modak-tamajit/Schedulix")

    def _show_about(self) -> None:
        w = ctk.CTkToplevel(self)
        w.title("About Schedulix")
        w.geometry("480x400")
        w.resizable(False, False)
        w.configure(fg_color=COLOR_PANEL)
        w.transient(self)
        w.grab_set()

        ctk.CTkLabel(
            w, text="Schedulix",
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(pady=(26, 2))

        ctk.CTkLabel(
            w, text="Advanced CPU Scheduling Simulator",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLOR_TEXT_MUTED,
        ).pack()

        ctk.CTkFrame(w, fg_color=COLOR_CARD_BORDER, height=1).pack(fill="x", padx=36, pady=16)

        lines = [
            ("Official Academic Project:", "CPU Scheduling Simulator"),
            ("Developer:", "Tamajit Modak"),
            ("Course:", "Operating Systems — Semester III"),
            ("Program:", "BCA (Hons.)"),
            ("Institution:", "Parul University, FITCS"),
            ("Academic Year:", "2026–27"),
            ("Technology Stack:", "Python 3.10+ • CustomTkinter • Matplotlib"),
        ]

        info_f = ctk.CTkFrame(w, fg_color="transparent")
        info_f.pack(padx=36, pady=4, fill="x")

        for key, val in lines:
            row = ctk.CTkFrame(info_f, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=key, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_MUTED, width=175, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_WHITE, anchor="w").pack(side="left")

        ctk.CTkButton(
            w, text="Close", width=110, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_ACCENT_BLUE, hover_color="#818CF8",
            text_color=COLOR_TEXT_WHITE, corner_radius=6, command=w.destroy,
        ).pack(pady=(22, 16))

    def _show_docs(self) -> None:
        w = ctk.CTkToplevel(self)
        w.title("Schedulix — Documentation & Reference Guide")
        w.geometry("660x540")
        w.configure(fg_color=COLOR_PANEL)
        w.transient(self)
        w.grab_set()

        scroll = ctk.CTkScrollableFrame(w, fg_color=COLOR_PANEL)
        scroll.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            scroll, text="Schedulix Quick Reference Guide",
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=COLOR_TEXT_WHITE,
        ).pack(anchor="w", pady=(0, 8))

        docs_content = [
            ("1. Supported Scheduling Algorithms",
             "• FCFS (First Come First Serve): Non-preemptive. Allocates CPU in arrival order.\n"
             "• SJF (Shortest Job First): Non-preemptive. Selects eligible job with shortest burst time.\n"
             "• SRTF (Shortest Remaining Time First): Preemptive SJF. Preempts current job if a newly arrived job has strictly shorter remaining time. Equal remaining time does not cause preemption.\n"
             "• Round Robin: Preemptive. Allocates a fixed time quantum. Arriving processes at quantum boundaries join before requeued jobs.\n"
             "• Priority Scheduling: Supports both Preemptive and Non-preemptive modes. Lower numerical value indicates higher priority (Priority 1 > Priority 2)."),

            ("2. Standard Performance Metrics & Formulas",
             "• Turnaround Time (TAT) = Completion Time (CT) − Arrival Time (AT)\n"
             "• Waiting Time (WT) = Turnaround Time (TAT) − Burst Time (BT)\n"
             "• Response Time (RT) = First CPU Allocation Time − Arrival Time (AT)\n"
             "• Throughput = Total Completed Processes / Total Simulation Time\n"
             "• CPU Utilization (%) = (Busy CPU Time / Total Simulation Time) × 100"),

            ("3. Tie-Breaking & Scheduling Conventions",
             "• Priority Convention: Lower integer = Higher priority.\n"
             "• Tie-Breaking Order: Earlier arrival time → input order → process ID.\n"
             "• SRTF Tie-Breaking: Equal remaining time does NOT trigger a preemptive context switch."),
        ]

        for sec_title, sec_body in docs_content:
            sec_card = ctk.CTkFrame(scroll, fg_color=COLOR_CARD, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
            sec_card.pack(fill="x", pady=6)
            ctk.CTkLabel(
                sec_card, text=sec_title,
                font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
                text_color=COLOR_ACCENT_BLUE,
            ).pack(anchor="w", padx=14, pady=(10, 4))
            ctk.CTkLabel(
                sec_card, text=sec_body, justify="left",
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=COLOR_TEXT_WHITE,
            ).pack(anchor="w", padx=14, pady=(0, 12))

        ctk.CTkButton(
            w, text="Close", width=110, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_ACCENT_BLUE, hover_color="#818CF8",
            text_color=COLOR_TEXT_WHITE, corner_radius=6, command=w.destroy,
        ).pack(pady=(0, 14))
