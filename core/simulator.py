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
    """Runs a CPU scheduling simulation on an isolated copy of the provided processes."""
    if not processes:
        raise ValueError("Add at least one process before running simulation.")

    # Guarantee isolated copy so caller workload is never modified
    workload_copy = [p.copy_for_simulation() for p in processes]

    algorithms = {
        "FCFS": lambda: schedule_fcfs(workload_copy),
        "SJF": lambda: schedule_sjf(workload_copy),
        "SRTF": lambda: schedule_srtf(workload_copy),
        "Round Robin": lambda: schedule_round_robin(workload_copy, quantum),
        "Priority": lambda: schedule_priority(workload_copy, priority_preemptive),
    }
    if algorithm not in algorithms:
        raise ValueError("Choose a valid scheduling algorithm.")

    simulated, segments = algorithms[algorithm]()
    return SimulationResult(
        algorithm,
        sorted(simulated, key=lambda p: p.order),
        segments,
        calculate_metrics(simulated, segments),
    )
