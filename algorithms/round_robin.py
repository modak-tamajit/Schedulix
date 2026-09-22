from __future__ import annotations

from collections import deque

from algorithms.common import Segment, append_segment, prepare
from models.process import Process


def schedule_round_robin(processes: list[Process], quantum: int) -> tuple[list[Process], list[Segment]]:
    if quantum <= 0: raise ValueError("Time quantum must be a positive integer.")
    items = prepare(processes); pending = sorted(items, key=lambda p: (p.arrival_time, p.order)); ready: deque[Process] = deque(); segments: list[Segment] = []; time = 0
    while pending or ready:
        if not ready and pending and time < pending[0].arrival_time:
            append_segment(segments, time, pending[0].arrival_time, "IDLE"); time = pending[0].arrival_time
        while pending and pending[0].arrival_time <= time: ready.append(pending.pop(0))
        p = ready.popleft()
        if p.start_time is None: p.start_time = time
        run = min(quantum, p.remaining_time); append_segment(segments, time, time + run, p.pid); time += run; p.remaining_time -= run
        # Arrivals at quantum end join before the running process is requeued.
        while pending and pending[0].arrival_time <= time: ready.append(pending.pop(0))
        if p.remaining_time: ready.append(p)
        else: p.completion_time = time
    return items, segments
