from __future__ import annotations

from algorithms.common import Segment, append_segment, prepare
from models.process import Process


def schedule_fcfs(processes: list[Process]) -> tuple[list[Process], list[Segment]]:
    items, segments, time = prepare(processes), [], 0
    for p in sorted(items, key=lambda x: (x.arrival_time, x.order, x.pid)):
        if time < p.arrival_time:
            append_segment(segments, time, p.arrival_time, "IDLE")
            time = p.arrival_time
        p.start_time = time
        time += p.burst_time
        p.remaining_time, p.completion_time = 0, time
        append_segment(segments, p.start_time, time, p.pid)
    return items, segments
