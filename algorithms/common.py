from __future__ import annotations

from collections.abc import Callable

from models.process import Process

Segment = tuple[int, int, str]


def prepare(processes: list[Process]) -> list[Process]:
    return [p.copy_for_simulation() for p in processes]


def finish(processes: list[Process], segments: list[Segment], current: int, process: Process) -> None:
    process.remaining_time = 0
    process.completion_time = current


def append_segment(segments: list[Segment], start: int, end: int, pid: str) -> None:
    if end > start:
        segments.append((start, end, pid))


def merge_contiguous(segments: list[Segment]) -> list[Segment]:
    """Remove arrival-only boundaries where the CPU never changed process."""
    merged: list[Segment] = []
    for start, end, pid in segments:
        if merged and merged[-1][1] == start and merged[-1][2] == pid:
            merged[-1] = (merged[-1][0], end, pid)
        else:
            merged.append((start, end, pid))
    return merged


def pick_ready(ready: list[Process], key: Callable[[Process], tuple]) -> Process:
    return min(ready, key=key)
