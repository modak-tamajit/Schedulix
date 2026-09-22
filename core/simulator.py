from __future__ import annotations

from dataclasses import dataclass

from algorithms import schedule_fcfs, schedule_priority, schedule_round_robin, schedule_sjf, schedule_srtf
from core.metrics import Summary, calculate_metrics
from models.process import Process


@dataclass
class SimulationResult:
    algorithm: str
    processes: list[Process]
    segments: list[tuple[int, int, str]]
    summary: Summary


def simulate(processes: list[Process], algorithm: str, quantum: int = 2, priority_preemptive: bool = False) -> SimulationResult:
    if not processes: raise ValueError("Add at least one process before running simulation.")
    algorithms = {
        "FCFS": lambda: schedule_fcfs(processes), "SJF": lambda: schedule_sjf(processes),
        "SRTF": lambda: schedule_srtf(processes), "Round Robin": lambda: schedule_round_robin(processes, quantum),
        "Priority": lambda: schedule_priority(processes, priority_preemptive),
    }
    if algorithm not in algorithms: raise ValueError("Choose a valid scheduling algorithm.")
    simulated, segments = algorithms[algorithm]()
    return SimulationResult(algorithm, sorted(simulated, key=lambda p: p.order), segments, calculate_metrics(simulated, segments))
