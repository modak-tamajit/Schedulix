from __future__ import annotations

from algorithms.common import Segment, append_segment, pick_ready, prepare
from models.process import Process


def schedule_sjf(processes: list[Process]) -> tuple[list[Process], list[Segment]]:
    items = prepare(processes)
    pending, segments, time = sorted(items, key=lambda p: (p.arrival_time, p.order)), [], 0
    ready: list[Process] = []
    while pending or ready:
        while pending and pending[0].arrival_time <= time:
            ready.append(pending.pop(0))
        if not ready:
            next_time = pending[0].arrival_time
            append_segment(segments, time, next_time, "IDLE")
            time = next_time
            continue
        p = pick_ready(ready, lambda x: (x.burst_time, x.arrival_time, x.order, x.pid))
        ready.remove(p); p.start_time = time
        time += p.burst_time; p.remaining_time = 0; p.completion_time = time
        append_segment(segments, p.start_time, time, p.pid)
    return items, segments
