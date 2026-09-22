from __future__ import annotations

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ── Schedulix Gantt chart palette ────────────────────────────────────
_BG_DEEP       = "#0D1117"
_BG_SURFACE    = "#161B22"
_BORDER        = "#30363D"
_TEXT_PRIMARY   = "#F0F6FC"
_TEXT_SECONDARY = "#8B949E"
_IDLE_COLOR    = "#30363D"

# Curated process colors — distinct, not oversaturated
PROCESS_COLORS = [
    "#6366F1",  # indigo
    "#10B981",  # emerald
    "#F59E0B",  # amber
    "#EC4899",  # pink
    "#06B6D4",  # cyan
    "#8B5CF6",  # violet
    "#F97316",  # orange
    "#14B8A6",  # teal
]


def draw_gantt(
    parent, segments: list[tuple[int, int, str]], title: str,
) -> FigureCanvasTkAgg:
    figure = Figure(figsize=(8, 2.8), dpi=100, facecolor=_BG_SURFACE)
    axis = figure.add_subplot(111)
    axis.set_facecolor(_BG_DEEP)

    # Map each unique PID to a consistent color
    pids_seen: list[str] = []
    for _, _, pid in segments:
        if pid != "IDLE" and pid not in pids_seen:
            pids_seen.append(pid)
    pid_color = {pid: PROCESS_COLORS[i % len(PROCESS_COLORS)] for i, pid in enumerate(pids_seen)}

    for start, end, pid in segments:
        color = _IDLE_COLOR if pid == "IDLE" else pid_color[pid]
        text_color = _TEXT_SECONDARY if pid == "IDLE" else _TEXT_PRIMARY
        axis.barh(
            0, end - start, left=start, height=0.55,
            color=color, edgecolor=_BG_DEEP, linewidth=1.2,
        )
        axis.text(
            (start + end) / 2, 0, pid,
            ha="center", va="center",
            color=text_color, fontweight="bold", fontsize=9,
        )

    ticks = sorted({v for s, e, _ in segments for v in (s, e)})
    axis.set_xticks(ticks)
    axis.set_yticks([])
    axis.set_xlabel("Time", color=_TEXT_SECONDARY, fontsize=10)
    axis.set_title(title, color=_TEXT_PRIMARY, fontsize=12, fontweight="bold", pad=10)
    axis.tick_params(colors=_TEXT_SECONDARY, labelsize=9)

    for spine in axis.spines.values():
        spine.set_color(_BORDER)

    figure.tight_layout()
    canvas = FigureCanvasTkAgg(figure, master=parent)
    canvas.draw()
    return canvas
