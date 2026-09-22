from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Sequence

from models.process import Process


def get_sample_workload() -> list[Process]:
    """Returns the 4-process quick demonstration workload matching the reference UI."""
    return [
        Process("P1", arrival_time=0, burst_time=5, priority=2, order=0),
        Process("P2", arrival_time=1, burst_time=3, priority=1, order=1),
        Process("P3", arrival_time=2, burst_time=8, priority=3, order=2),
        Process("P4", arrival_time=3, burst_time=6, priority=1, order=3),
    ]


def get_academic_workload() -> list[Process]:
    """Returns the 5-process benchmark workload used in the academic report."""
    return [
        Process("P1", arrival_time=0, burst_time=4, priority=2, order=0),
        Process("P2", arrival_time=1, burst_time=3, priority=1, order=1),
        Process("P3", arrival_time=2, burst_time=1, priority=4, order=2),
        Process("P4", arrival_time=3, burst_time=5, priority=3, order=3),
        Process("P5", arrival_time=4, burst_time=2, priority=5, order=4),
    ]


def export_workload(processes: Sequence[Process], filepath: str | Path) -> None:
    """Exports a list of processes to a JSON or CSV file based on file extension."""
    path = Path(filepath)
    ext = path.suffix.lower()

    if ext == ".json":
        data = [
            {
                "pid": p.pid,
                "arrival_time": p.arrival_time,
                "burst_time": p.burst_time,
                "priority": p.priority,
            }
            for p in processes
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    elif ext == ".csv":
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["pid", "arrival_time", "burst_time", "priority"])
            for p in processes:
                writer.writerow([p.pid, p.arrival_time, p.burst_time, p.priority])
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Please use .json or .csv.")


def import_workload(filepath: str | Path) -> list[Process]:
    """Imports and validates a list of processes from a JSON or CSV file."""
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {filepath}")

    ext = path.suffix.lower()
    processes: list[Process] = []

    if ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as err:
                raise ValueError(f"Invalid JSON file: {err}") from err

        if not isinstance(data, list):
            raise ValueError("JSON file must contain an array of process objects.")

        seen_pids: set[str] = set()
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Process at index {idx} must be an object.")
            pid = str(item.get("pid", "")).strip()
            if not pid:
                raise ValueError(f"Process at index {idx} has an empty PID.")
            if pid in seen_pids:
                raise ValueError(f"Duplicate PID '{pid}' found in workload.")
            seen_pids.add(pid)

            try:
                at = int(item.get("arrival_time", 0))
                bt = int(item.get("burst_time", 1))
                priority = int(item.get("priority", 1))
            except (ValueError, TypeError) as err:
                raise ValueError(f"Process '{pid}' contains invalid non-integer attributes: {err}") from err

            if at < 0:
                raise ValueError(f"Process '{pid}' has negative arrival time ({at}).")
            if bt <= 0:
                raise ValueError(f"Process '{pid}' has non-positive burst time ({bt}).")
            if priority <= 0:
                raise ValueError(f"Process '{pid}' has non-positive priority ({priority}).")

            processes.append(Process(pid, arrival_time=at, burst_time=bt, priority=priority, order=idx))

    elif ext == ".csv":
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV file is empty.")

            normalized_fields = {fn.strip().lower(): fn for fn in reader.fieldnames if fn}
            required = ["pid", "arrival_time", "burst_time"]
            missing = [r for r in required if r not in normalized_fields]
            if missing:
                raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

            pid_col = normalized_fields["pid"]
            at_col = normalized_fields["arrival_time"]
            bt_col = normalized_fields["burst_time"]
            pr_col = normalized_fields.get("priority")

            seen_pids: set[str] = set()
            for idx, row in enumerate(reader):
                pid = str(row.get(pid_col, "")).strip()
                if not pid:
                    raise ValueError(f"CSV row {idx + 2} has an empty PID.")
                if pid in seen_pids:
                    raise ValueError(f"Duplicate PID '{pid}' in CSV row {idx + 2}.")
                seen_pids.add(pid)

                try:
                    at = int(row.get(at_col, "0").strip())
                    bt = int(row.get(bt_col, "1").strip())
                    priority = int(row.get(pr_col, "1").strip()) if pr_col and row.get(pr_col) else 1
                except ValueError as err:
                    raise ValueError(f"CSV row {idx + 2} (PID '{pid}') has invalid numeric values: {err}") from err

                if at < 0:
                    raise ValueError(f"Process '{pid}' has negative arrival time ({at}).")
                if bt <= 0:
                    raise ValueError(f"Process '{pid}' has non-positive burst time ({bt}).")
                if priority <= 0:
                    raise ValueError(f"Process '{pid}' has non-positive priority ({priority}).")

                processes.append(Process(pid, arrival_time=at, burst_time=bt, priority=priority, order=idx))
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Please use .json or .csv.")

    if not processes:
        raise ValueError("Workload contains no processes.")

    return processes
