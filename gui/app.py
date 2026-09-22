from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from core.simulator import SimulationResult, simulate
from gui.gantt_chart import draw_gantt
from gui.process_table import create_process_table, apply_table_theme
from gui.results_view import create_results_table

from models.process import Process

# ── Schedulix Color Palette ──────────────────────────────────────────
BG_DEEP       = "#0D1117"
BG_SURFACE    = "#161B22"
BG_CARD       = "#1C2333"
BORDER        = "#30363D"
ACCENT        = "#6366F1"
ACCENT_HOVER  = "#818CF8"
SUCCESS       = "#10B981"
DANGER        = "#F43F5E"
TEXT_PRIMARY   = "#F0F6FC"
TEXT_SECONDARY = "#8B949E"

FONT_FAMILY = ("Inter", "Segoe UI", "sans-serif")

ALGORITHM_INFO = {
    "FCFS": "Non-preemptive. Runs in arrival order. Can cause convoy effect.",
    "SJF": "Non-preemptive. Chooses shortest available burst. Needs burst-time knowledge.",
    "SRTF": "Preemptive SJF. Chooses shortest remaining time. May cause more context switches.",
    "Round Robin": "Preemptive. Uses time quantum. Designed for time-sharing systems.",
    "Priority": "Priority-based. Lower number = higher priority. Choose preemptive or non-preemptive mode.",
}


class SchedulerApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Schedulix")
        self.geometry("1320x860")
        self.minsize(1060, 740)
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=BG_DEEP)

        self.processes: list[Process] = []
        self.chart = None
        self.results: dict[str, SimulationResult] = {}
        self.algorithm = ctk.StringVar(value="FCFS")
        self.priority_mode = ctk.StringVar(value="Non-preemptive")

        self._build()
        self._refresh_processes()

    # ── Layout ────────────────────────────────────────────────────────
    def _build(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ───────────────────────────────────────────────────
        header_frame = ctk.CTkFrame(self, fg_color=BG_SURFACE, corner_radius=0)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        title_block = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_block.grid(row=0, column=0, padx=24, pady=(14, 12), sticky="w")

        ctk.CTkLabel(
            title_block, text="Schedulix",
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=28, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_block, text="Advanced CPU Scheduling Simulator",
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=13),
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w", pady=(1, 0))

        # About button (right side of header)
        ctk.CTkButton(
            header_frame, text="About", width=72, height=30,
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
            fg_color=BG_CARD, hover_color=BORDER,
            border_width=1, border_color=BORDER,
            text_color=TEXT_SECONDARY, corner_radius=6,
            command=self._show_about,
        ).grid(row=0, column=1, padx=24, pady=14, sticky="e")

        # Accent line under header
        ctk.CTkFrame(
            self, fg_color=ACCENT, height=2, corner_radius=0,
        ).grid(row=0, column=0, columnspan=2, sticky="sew")

        # ── Sidebar (Left Panel) ─────────────────────────────────────
        left = ctk.CTkFrame(self, fg_color=BG_SURFACE, corner_radius=10, border_width=1, border_color=BORDER)
        left.grid(row=1, column=0, padx=(16, 8), pady=12, sticky="ns")

        # ── Main Content (Right Panel) ───────────────────────────────
        right = ctk.CTkScrollableFrame(self, fg_color=BG_DEEP, corner_radius=0)
        right.grid(row=1, column=1, padx=(8, 16), pady=12, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        self.right_panel = right

        # Build main first (creates self.info), then sidebar (references it)
        self._build_main(right)
        self._build_sidebar(left)

    # ── Sidebar ───────────────────────────────────────────────────────
    def _build_sidebar(self, parent: ctk.CTkFrame) -> None:
        pad_x = 14

        # Section: Process Input
        self._section_label(parent, "Process Input")

        self.entries: dict[str, ctk.CTkEntry] = {}
        fields = [
            ("PID", "e.g. P1"),
            ("Arrival Time", "≥ 0"),
            ("Burst Time", "> 0"),
            ("Priority", "> 0 (lower = higher)"),
        ]
        for label_text, placeholder in fields:
            ctk.CTkLabel(
                parent, text=label_text,
                font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
                text_color=TEXT_SECONDARY,
            ).pack(padx=pad_x, anchor="w", pady=(6, 1))

            entry = ctk.CTkEntry(
                parent, width=240, height=32,
                font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
                fg_color=BG_CARD, border_color=BORDER,
                text_color=TEXT_PRIMARY, corner_radius=6,
                placeholder_text=placeholder,
                placeholder_text_color=TEXT_SECONDARY,
            )
            entry.pack(padx=pad_x, pady=(0, 2))
            self.entries[label_text] = entry

        # Buttons: Add / Update / Delete
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(padx=pad_x, pady=(8, 2), fill="x")

        self._make_button(btn_frame, "Add Process", ACCENT, ACCENT_HOVER, self.add_process).pack(fill="x", pady=2)
        self._make_button(btn_frame, "Update Selected", BG_CARD, BORDER, self.update_process).pack(fill="x", pady=2)
        self._make_button(btn_frame, "Delete Selected", BG_CARD, BORDER, self.delete_process).pack(fill="x", pady=2)
        self._make_button(btn_frame, "Clear All", DANGER, "#E11D48", self.clear_processes).pack(fill="x", pady=2)

        # Divider
        ctk.CTkFrame(parent, fg_color=BORDER, height=1).pack(fill="x", padx=pad_x, pady=(12, 4))

        # Section: Scheduling Controls
        self._section_label(parent, "Scheduling Controls")

        ctk.CTkLabel(
            parent, text="Algorithm",
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
            text_color=TEXT_SECONDARY,
        ).pack(padx=pad_x, anchor="w", pady=(6, 1))

        ctk.CTkOptionMenu(
            parent, values=list(ALGORITHM_INFO), variable=self.algorithm,
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
            fg_color=BG_CARD, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            dropdown_fg_color=BG_CARD, dropdown_hover_color=BORDER,
            text_color=TEXT_PRIMARY, corner_radius=6,
            command=lambda _: self._on_algorithm_change(),
        ).pack(padx=pad_x, pady=2, fill="x")

        # Priority mode (always visible, relevant for Priority algorithm)
        ctk.CTkLabel(
            parent, text="Priority Mode",
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
            text_color=TEXT_SECONDARY,
        ).pack(padx=pad_x, anchor="w", pady=(6, 1))

        ctk.CTkOptionMenu(
            parent, values=["Non-preemptive", "Preemptive"], variable=self.priority_mode,
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
            fg_color=BG_CARD, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            dropdown_fg_color=BG_CARD, dropdown_hover_color=BORDER,
            text_color=TEXT_PRIMARY, corner_radius=6,
        ).pack(padx=pad_x, pady=2, fill="x")

        # Time Quantum (shown/hidden based on algorithm)
        self.quantum_label = ctk.CTkLabel(
            parent, text="Time Quantum",
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
            text_color=TEXT_SECONDARY,
        )

        self.quantum = ctk.CTkEntry(
            parent, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
            fg_color=BG_CARD, border_color=BORDER,
            text_color=TEXT_PRIMARY, corner_radius=6,
            placeholder_text="e.g. 2",
            placeholder_text_color=TEXT_SECONDARY,
        )
        self.quantum.insert(0, "2")

        # Initially hidden (FCFS is default)
        self._on_algorithm_change()

        # Divider
        ctk.CTkFrame(parent, fg_color=BORDER, height=1).pack(fill="x", padx=pad_x, pady=(12, 4))

        # Run / Compare / Reset
        self._section_label(parent, "Actions")

        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(padx=pad_x, pady=(4, 14), fill="x")

        self._make_button(action_frame, "▶  Run Simulation", ACCENT, ACCENT_HOVER, self.run).pack(fill="x", pady=2)
        self._make_button(action_frame, "Compare All Algorithms", SUCCESS, "#059669", self.compare).pack(fill="x", pady=2)
        self._make_button(action_frame, "Reset Results", BG_CARD, BORDER, self.reset_results).pack(fill="x", pady=2)

    # ── Main Content Area ─────────────────────────────────────────────
    def _build_main(self, parent: ctk.CTkScrollableFrame) -> None:
        # Algorithm info bar
        self.info = ctk.CTkLabel(
            parent, text="", justify="left", wraplength=800,
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
            text_color=TEXT_SECONDARY,
        )
        self.info.grid(row=0, column=0, padx=4, pady=(4, 8), sticky="w")
        self._update_info()

        # ── Input Workload card ──────────────────────────────────────
        workload_card = self._card(parent, "Input Workload")
        workload_card.grid(row=1, column=0, padx=0, pady=(0, 10), sticky="ew")

        self.process_table = create_process_table(workload_card)
        self.process_table.pack(fill="x", padx=12, pady=(4, 12))
        self.process_table.bind("<<TreeviewSelect>>", self.load_selected)

        # ── Gantt Chart card ─────────────────────────────────────────
        gantt_card = self._card(parent, "Gantt Chart")
        gantt_card.grid(row=2, column=0, padx=0, pady=(0, 10), sticky="ew")

        self.chart_frame = ctk.CTkFrame(gantt_card, fg_color="transparent")
        self.chart_frame.pack(fill="x", padx=12, pady=(4, 12))

        # ── Results card ─────────────────────────────────────────────
        results_card = self._card(parent, "Results")
        results_card.grid(row=3, column=0, padx=0, pady=(0, 10), sticky="ew")

        self.results_table = create_results_table(results_card)
        self.results_table.pack(fill="x", padx=12, pady=(4, 8))

        # ── Metrics card ─────────────────────────────────────────────
        metrics_card = self._card(parent, "Aggregate Metrics")
        metrics_card.grid(row=4, column=0, padx=0, pady=(0, 10), sticky="ew")

        self.metrics_frame = ctk.CTkFrame(metrics_card, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=12, pady=(4, 12))

        self.summary = ctk.CTkLabel(
            self.metrics_frame,
            text="Run a simulation to view metrics.",
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=13),
            text_color=TEXT_SECONDARY, justify="left",
        )
        self.summary.pack(anchor="w")

    # ── Helper: section label ─────────────────────────────────────────
    def _section_label(self, parent: ctk.CTkFrame, text: str) -> None:
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=13, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(padx=14, pady=(14, 2), anchor="w")

    # ── Helper: styled button ─────────────────────────────────────────
    def _make_button(
        self, parent, text: str, fg: str, hover: str, command,
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent, text=text, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=12, weight="bold"),
            fg_color=fg, hover_color=hover,
            text_color=TEXT_PRIMARY, corner_radius=6,
            command=command,
        )

    # ── Helper: content card ──────────────────────────────────────────
    def _card(self, parent, title: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent, fg_color=BG_SURFACE, corner_radius=10,
            border_width=1, border_color=BORDER,
        )
        ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(padx=12, pady=(12, 4), anchor="w")
        return card

    # ── Algorithm change handler ──────────────────────────────────────
    def _on_algorithm_change(self) -> None:
        self._update_info()
        if self.algorithm.get() == "Round Robin":
            self.quantum_label.pack(padx=14, anchor="w", pady=(6, 1))
            self.quantum.pack(padx=14, pady=2, fill="x")
        else:
            self.quantum_label.pack_forget()
            self.quantum.pack_forget()

    def _update_info(self) -> None:
        algo = self.algorithm.get()
        info_text = ALGORITHM_INFO[algo]
        self.info.configure(
            text=f"ℹ  {algo}:  {info_text}  •  Priority convention: lower value = higher priority."
        )

    # ── About dialog ──────────────────────────────────────────────────
    def _show_about(self) -> None:
        window = ctk.CTkToplevel(self)
        window.title("About Schedulix")
        window.geometry("420x300")
        window.resizable(False, False)
        window.configure(fg_color=BG_SURFACE)
        window.transient(self)
        window.grab_set()

        ctk.CTkLabel(
            window, text="Schedulix",
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=24, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(28, 2))

        ctk.CTkLabel(
            window, text="Advanced CPU Scheduling Simulator",
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=13),
            text_color=TEXT_SECONDARY,
        ).pack()

        ctk.CTkFrame(window, fg_color=BORDER, height=1).pack(fill="x", padx=40, pady=16)

        for line in [
            "Developed by  Tamajit Modak",
            "",
            "BCA (Hons.) — Semester III",
            "Operating Systems",
            "Parul University, FITCS",
            "",
            "Python  •  CustomTkinter  •  Matplotlib",
        ]:
            ctk.CTkLabel(
                window, text=line,
                font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
                text_color=TEXT_PRIMARY if line and not line.startswith("Python") else TEXT_SECONDARY,
            ).pack(pady=1)

        ctk.CTkButton(
            window, text="Close", width=100, height=30,
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY, corner_radius=6,
            command=window.destroy,
        ).pack(pady=(16, 20))

    # ── Input validation ──────────────────────────────────────────────
    def _valid_input(self, allow_selected: bool = False) -> tuple[str, int, int, int]:
        pid = self.entries["PID"].get().strip()
        if not pid:
            raise ValueError("PID cannot be empty.")

        values: list[int] = []
        for label in ("Arrival Time", "Burst Time", "Priority"):
            raw = self.entries[label].get().strip()
            try:
                values.append(int(raw))
            except ValueError:
                raise ValueError(f"{label} must be an integer.")

        at, bt, priority = values
        if at < 0:
            raise ValueError("Arrival Time must be non-negative (≥ 0).")
        if bt <= 0:
            raise ValueError("Burst Time must be a positive integer (> 0).")
        if priority <= 0:
            raise ValueError("Priority must be a positive integer (> 0). Lower number = higher priority.")

        selected = self.process_table.selection()
        if any(p.pid == pid for p in self.processes) and not (
            allow_selected and selected and self.processes[int(selected[0])].pid == pid
        ):
            raise ValueError(f"PID \"{pid}\" already exists. Each process must have a unique identifier.")

        return pid, at, bt, priority

    # ── CRUD operations ───────────────────────────────────────────────
    def add_process(self) -> None:
        try:
            pid, at, bt, priority = self._valid_input()
            self.processes.append(Process(pid, at, bt, priority, order=len(self.processes)))
            self._refresh_processes()
            self._clear_entries()
        except ValueError as error:
            messagebox.showerror("Invalid Process", str(error))

    def update_process(self) -> None:
        selected = self.process_table.selection()
        if not selected:
            return messagebox.showinfo("Select Process", "Select a process from the table to update.")
        try:
            pid, at, bt, priority = self._valid_input(True)
            index = int(selected[0])
            self.processes[index] = Process(pid, at, bt, priority, order=index)
            self._refresh_processes()
            self._clear_entries()
        except ValueError as error:
            messagebox.showerror("Invalid Process", str(error))

    def delete_process(self) -> None:
        selected = self.process_table.selection()
        if not selected:
            return messagebox.showinfo("Select Process", "Select a process from the table to delete.")
        self.processes.pop(int(selected[0]))
        self._renumber()
        self._refresh_processes()

    def clear_processes(self) -> None:
        self.processes.clear()
        self._refresh_processes()
        self.reset_results()

    def _renumber(self) -> None:
        for index, p in enumerate(self.processes):
            p.order = index

    def _clear_entries(self) -> None:
        for entry in self.entries.values():
            entry.delete(0, "end")

    def _refresh_processes(self) -> None:
        self.process_table.delete(*self.process_table.get_children())
        for index, p in enumerate(self.processes):
            tag = "even" if index % 2 == 0 else "odd"
            self.process_table.insert(
                "", "end", iid=str(index),
                values=(p.pid, p.arrival_time, p.burst_time, p.priority),
                tags=(tag,),
            )

    def load_selected(self, _event=None) -> None:
        selected = self.process_table.selection()
        if selected:
            p = self.processes[int(selected[0])]
            self._clear_entries()
            for key, value in zip(self.entries, (p.pid, p.arrival_time, p.burst_time, p.priority)):
                self.entries[key].insert(0, str(value))

    # ── Simulation ────────────────────────────────────────────────────
    def _quantum_value(self) -> int:
        try:
            quantum = int(self.quantum.get())
            if quantum <= 0:
                raise ValueError
            return quantum
        except ValueError:
            raise ValueError("Time Quantum must be a positive integer (> 0).")

    def _algo_display_name(self) -> str:
        algo = self.algorithm.get()
        if algo == "Priority":
            return f"Priority ({self.priority_mode.get()})"
        return algo

    def run(self) -> None:
        try:
            result = simulate(
                self.processes, self.algorithm.get(),
                self._quantum_value(),
                self.priority_mode.get() == "Preemptive",
            )
            self.results[self._algo_display_name()] = result
            self._show_result(result)
        except ValueError as error:
            messagebox.showerror("Simulation Error", str(error))

    def _show_result(self, result: SimulationResult) -> None:
        # Results table
        self.results_table.delete(*self.results_table.get_children())
        for i, p in enumerate(result.processes):
            tag = "even" if i % 2 == 0 else "odd"
            self.results_table.insert(
                "", "end",
                values=(
                    p.pid, p.arrival_time, p.burst_time, p.priority,
                    p.completion_time, p.turnaround_time,
                    p.waiting_time, p.response_time,
                ),
                tags=(tag,),
            )

        # Gantt chart
        if self.chart:
            self.chart.get_tk_widget().destroy()
        self.chart = draw_gantt(
            self.chart_frame, result.segments,
            f"Gantt Chart — {self._algo_display_name()}",
        )
        self.chart.get_tk_widget().pack(fill="x", padx=4, pady=4)

        # Metrics
        self._show_metrics(result)

    def _show_metrics(self, result: SimulationResult) -> None:
        s = result.summary
        # Destroy old metric widgets
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()

        metrics_grid = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        metrics_grid.pack(fill="x")

        metrics = [
            ("Avg Waiting Time", f"{s.average_waiting_time:.2f}"),
            ("Avg Turnaround Time", f"{s.average_turnaround_time:.2f}"),
            ("Avg Response Time", f"{s.average_response_time:.2f}"),
            ("Throughput", f"{s.throughput:.3f} proc/unit"),
            ("Total Time", f"{s.total_time}"),
            ("CPU Utilization", f"{s.cpu_utilization:.2f}%"),
        ]

        for col, (label, value) in enumerate(metrics):
            metrics_grid.grid_columnconfigure(col, weight=1)
            cell = ctk.CTkFrame(
                metrics_grid, fg_color=BG_CARD, corner_radius=8,
                border_width=1, border_color=BORDER,
            )
            cell.grid(row=0, column=col, padx=4, pady=4, sticky="ew")

            ctk.CTkLabel(
                cell, text=value,
                font=ctk.CTkFont(family=FONT_FAMILY[0], size=18, weight="bold"),
                text_color=ACCENT,
            ).pack(padx=10, pady=(10, 2))

            ctk.CTkLabel(
                cell, text=label,
                font=ctk.CTkFont(family=FONT_FAMILY[0], size=10),
                text_color=TEXT_SECONDARY,
            ).pack(padx=10, pady=(0, 10))

    # ── Compare all algorithms ────────────────────────────────────────
    def compare(self) -> None:
        try:
            q = self._quantum_value()
            configs = [
                ("FCFS", False), ("SJF", False), ("SRTF", False),
                ("Round Robin", False),
                ("Priority", False), ("Priority", True),
            ]
            self.results = {}
            for name, pre in configs:
                display = name if name != "Priority" else f"Priority ({'Preemptive' if pre else 'Non-preemptive'})"
                self.results[display] = simulate(self.processes, name, q, pre)

            window = ctk.CTkToplevel(self)
            window.title("Schedulix — Algorithm Comparison")
            window.geometry("900x460")
            window.configure(fg_color=BG_SURFACE)
            window.transient(self)

            ctk.CTkLabel(
                window, text="Algorithm Comparison",
                font=ctk.CTkFont(family=FONT_FAMILY[0], size=18, weight="bold"),
                text_color=TEXT_PRIMARY,
            ).pack(padx=24, pady=(20, 4), anchor="w")

            ctk.CTkLabel(
                window, text="Results are based on the current workload. Performance varies by workload.",
                font=ctk.CTkFont(family=FONT_FAMILY[0], size=11),
                text_color=TEXT_SECONDARY,
            ).pack(padx=24, anchor="w")

            # Comparison table
            header = f"{'Algorithm':<35} {'Avg WT':>8} {'Avg TAT':>9} {'Avg RT':>8} {'Throughput':>11} {'CPU Util.':>10}"
            separator = "─" * 85
            lines = [header, separator]
            for name, result in self.results.items():
                s = result.summary
                lines.append(
                    f"{name:<35} {s.average_waiting_time:>8.2f} {s.average_turnaround_time:>9.2f} "
                    f"{s.average_response_time:>8.2f} {s.throughput:>11.3f} {s.cpu_utilization:>9.2f}%"
                )

            ctk.CTkLabel(
                window, text="\n".join(lines), justify="left",
                font=ctk.CTkFont(family="Consolas", size=12),
                text_color=TEXT_PRIMARY,
            ).pack(padx=24, pady=(12, 8), anchor="w")

            # Selector to view Gantt chart
            ctk.CTkFrame(window, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=8)

            select_frame = ctk.CTkFrame(window, fg_color="transparent")
            select_frame.pack(padx=24, pady=4, fill="x")

            choice = ctk.StringVar(value=next(iter(self.results)))
            ctk.CTkOptionMenu(
                select_frame, values=list(self.results), variable=choice,
                font=ctk.CTkFont(family=FONT_FAMILY[0], size=12),
                fg_color=BG_CARD, button_color=ACCENT,
                button_hover_color=ACCENT_HOVER,
                dropdown_fg_color=BG_CARD, dropdown_hover_color=BORDER,
                text_color=TEXT_PRIMARY, corner_radius=6,
                width=280,
            ).pack(side="left", padx=(0, 8))

            ctk.CTkButton(
                select_frame, text="Show Gantt Chart", height=32,
                font=ctk.CTkFont(family=FONT_FAMILY[0], size=12, weight="bold"),
                fg_color=ACCENT, hover_color=ACCENT_HOVER,
                text_color=TEXT_PRIMARY, corner_radius=6,
                command=lambda: self._show_result(self.results[choice.get()]),
            ).pack(side="left")

        except ValueError as error:
            messagebox.showerror("Comparison Error", str(error))

    # ── Reset ─────────────────────────────────────────────────────────
    def reset_results(self) -> None:
        self.results_table.delete(*self.results_table.get_children())
        if self.chart:
            self.chart.get_tk_widget().destroy()
            self.chart = None
        # Reset metrics display
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        self.summary = ctk.CTkLabel(
            self.metrics_frame,
            text="Results reset. Input workload kept.",
            font=ctk.CTkFont(family=FONT_FAMILY[0], size=13),
            text_color=TEXT_SECONDARY, justify="left",
        )
        self.summary.pack(anchor="w")
