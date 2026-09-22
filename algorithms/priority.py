from __future__ import annotations

from algorithms.common import Segment, append_segment, merge_contiguous, pick_ready, prepare
from models.process import Process


def schedule_priority(processes: list[Process], preemptive: bool = False) -> tuple[list[Process], list[Segment]]:
    items = prepare(processes); pending = sorted(items, key=lambda p: (p.arrival_time, p.order)); ready: list[Process] = []; segments: list[Segment] = []; time = 0
    while pending or ready:
        while pending and pending[0].arrival_time <= time: ready.append(pending.pop(0))
        if not ready:
            next_time = pending[0].arrival_time; append_segment(segments, time, next_time, "IDLE"); time = next_time; continue
        p = pick_ready(ready, lambda x: (x.priority, x.arrival_time, x.order, x.pid)); ready.remove(p)
        if p.start_time is None: p.start_time = time
        run = p.remaining_time if not preemptive else min(p.remaining_time, (pending[0].arrival_time - time) if pending else p.remaining_time)
        append_segment(segments, time, time + run, p.pid); time += run; p.remaining_time -= run
        if p.remaining_time: ready.append(p)
        else: p.completion_time = time
    return items, merge_contiguous(segments)
