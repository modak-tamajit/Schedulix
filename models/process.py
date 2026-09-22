from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int
    remaining_time: int | None = None
    start_time: int | None = None
    completion_time: int | None = None
    turnaround_time: int | None = None
    waiting_time: int | None = None
    response_time: int | None = None
    order: int = 0

    def __post_init__(self) -> None:
        if self.remaining_time is None:
            self.remaining_time = self.burst_time

    def copy_for_simulation(self) -> "Process":
        return Process(self.pid, self.arrival_time, self.burst_time, self.priority, order=self.order)
