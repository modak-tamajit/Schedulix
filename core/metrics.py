from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from models.process import Process


@dataclass(frozen=True)
class Summary:
    average_waiting_time: float
    average_turnaround_time: float
    average_response_time: float
    throughput: float
    total_time: int
    cpu_utilization: float


def calculate_metrics(processes: Iterable[Process], segments: list[tuple[int, int, str]]) -> Summary:
    items = list(processes)
    for p in items:
        assert p.completion_time is not None and p.start_time is not None
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        p.response_time = p.start_time - p.arrival_time
    # The simulator's clock starts at 0, so initial idle time counts in totals.
    end = max((end for _, end, _ in segments), default=0)
    total = end
    busy = sum(end - begin for begin, end, pid in segments if pid != "IDLE")
    count = len(items)
    return Summary(
        sum(p.waiting_time or 0 for p in items) / count if count else 0,
        sum(p.turnaround_time or 0 for p in items) / count if count else 0,
        sum(p.response_time or 0 for p in items) / count if count else 0,
        count / total if total else 0,
        total,
        busy / total * 100 if total else 0,
    )
