from __future__ import annotations

from typing import Mapping
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from core.simulator import SimulationResult

_BG_DEEP        = "#121214"
_BG_SURFACE     = "#17171A"
_BORDER         = "#2C2D35"
_TEXT_PRIMARY   = "#FFFFFF"
_TEXT_SECONDARY = "#8A909D"
_BAR_WT         = "#6366F1"   # Indigo for Average Waiting Time
_BAR_TAT        = "#10B981"   # Emerald for Average Turnaround Time


def draw_comparison_chart(parent, results: Mapping[str, SimulationResult]) -> FigureCanvasTkAgg:
    """Draws a grouped bar chart comparing Average Waiting Time and Turnaround Time across algorithms."""
    figure = Figure(figsize=(8.5, 3.4), dpi=100, facecolor=_BG_SURFACE)
    ax = figure.add_subplot(111)
    ax.set_facecolor(_BG_DEEP)

    labels = list(results.keys())
    # Shorten long labels for display if needed
    display_labels = [
        label.replace("Priority (Non-preemptive)", "Priority (NP)")
             .replace("Priority (Preemptive)", "Priority (P)")
             .replace("Round Robin", "Round Robin")
        for label in labels
    ]

    avg_wt = [results[k].summary.average_waiting_time for k in labels]
    avg_tat = [results[k].summary.average_turnaround_time for k in labels]

    x = np.arange(len(labels))
    width = 0.35

    rects1 = ax.bar(x - width / 2, avg_wt, width, label="Avg Waiting Time", color=_BAR_WT, edgecolor=_BG_DEEP)
    rects2 = ax.bar(x + width / 2, avg_tat, width, label="Avg Turnaround Time", color=_BAR_TAT, edgecolor=_BG_DEEP)

    # Value labels on top of bars
    for rect in list(rects1) + list(rects2):
        height = rect.get_height()
        ax.annotate(
            f"{height:.1f}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=8, color=_TEXT_SECONDARY, fontweight="bold",
        )

    ax.set_ylabel("Time Units", color=_TEXT_SECONDARY, fontsize=10)
    ax.set_title("Algorithm Performance Comparison (Same Workload)", color=_TEXT_PRIMARY, fontsize=11, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(display_labels, color=_TEXT_SECONDARY, fontsize=9)
    ax.tick_params(colors=_TEXT_SECONDARY)

    legend = ax.legend(facecolor=_BG_SURFACE, edgecolor=_BORDER, fontsize=9)
    for text in legend.get_texts():
        text.set_color(_TEXT_PRIMARY)

    ax.grid(axis="y", linestyle="--", alpha=0.25, color=_BORDER)
    for spine in ax.spines.values():
        spine.set_color(_BORDER)

    figure.tight_layout()
    canvas = FigureCanvasTkAgg(figure, master=parent)
    canvas.draw()
    return canvas
