
# Schedulix

**Advanced CPU Scheduling Simulator**

Developed by **Tamajit Modak**

A desktop CPU scheduling simulator built with Python, CustomTkinter, and Matplotlib. This project was developed as part of the BCA (Hons.) Semester III Operating Systems coursework at Parul University, FITCS.

Schedulix allows users to create process workloads, run different CPU scheduling algorithms, view execution timelines through Gantt charts, and analyze scheduling performance using standard operating system metrics.

## Overview

CPU scheduling determines how processes are assigned to the CPU and in what order they are executed. Different scheduling algorithms produce different waiting times, response times, and completion times.

This project provides an interactive way to study and compare these algorithms without manually calculating every execution step.

## Features

- Create and manage process workloads.
- Add, edit, delete, and clear processes.
- Retain the current workload while resetting simulation results.
- Simulate multiple CPU scheduling algorithms.
- View process-level scheduling metrics.
- Generate Gantt charts using Matplotlib.
- Display CPU idle periods in execution timelines.
- Compare scheduling algorithms using the same workload.
- Select a specific algorithm's Gantt chart during comparison.
- Validate user inputs before running simulations.
- View algorithm-related information for viva preparation.
- Professional dark developer-dashboard interface.
- About section with developer and academic attribution.

## Supported Scheduling Algorithms

| Algorithm | Type | Description |
|---|---|---|
| FCFS | Non-preemptive | Executes processes according to their arrival order. |
| SJF | Non-preemptive | Selects the available process with the shortest burst time. |
| SRTF | Preemptive | Selects the process with the shortest remaining execution time. |
| Round Robin | Preemptive | Uses time slicing and a FIFO ready queue. |
| Priority | Both modes | Selects processes based on priority, with support for preemptive and non-preemptive scheduling. |

### Scheduling Rules

The simulator follows the rules below when selecting processes:

- A smaller priority number indicates a higher priority. For example, Priority 1 is higher than Priority 2.
- When multiple candidates are eligible, the selection order is:
  1. Earlier arrival time.
  2. Input order.
  3. Process ID (PID).
- SRTF does not replace the currently running process when a newly arrived process has the same remaining time.
- In Round Robin, processes arriving at a time quantum boundary are added to the FIFO queue before the expired process is requeued.

These rules help maintain consistent and predictable scheduling results.

## Scheduling Metrics

The simulator calculates the following metrics for each process.

| Metric | Formula | Description |
|---|---|---|
| Completion Time (CT) | — | Time at which the process finishes execution. |
| Turnaround Time (TAT) | `CT - AT` | Total time taken by a process from arrival to completion. |
| Waiting Time (WT) | `TAT - BT` | Time spent waiting in the ready queue. |
| Response Time (RT) | `First CPU Allocation - AT` | Time between arrival and the process's first CPU allocation. |

### Aggregate Metrics

#### Throughput

Measures the number of completed processes per unit of total simulation time.

```text
Throughput = Completed Processes / Total Simulation Time
```

#### CPU Utilization

Measures the percentage of the total simulation time during which the CPU is busy.

```text
CPU Utilization = (Busy CPU Time / Total Simulation Time) × 100
```

**Simulation time:** The clock starts at `0` and ends when the final process completes.

**Busy CPU time:** Includes time spent executing processes and excludes explicit `IDLE` segments in the Gantt chart, including initial CPU idle time.

## Technology Stack

- **Python 3.10+** — Core programming language.
- **CustomTkinter** — Desktop GUI development.
- **Matplotlib** — Gantt chart generation and visualization.
- **unittest** — Automated testing.

## Installation

### Prerequisites

- Python 3.10 or newer
- pip
- A desktop environment that supports Tkinter

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

Replace the repository URL and folder name with your actual project details.

### 2. Install Dependencies

```powershell
py -m pip install -r requirements.txt
```

### 3. Run the Application

**Development mode** (with terminal output):

```powershell
py main.py
```

**Windows console-free mode** (no terminal window):

Double-click `main.pyw`, or run:

```powershell
pythonw main.pyw
```

> **Note:** The `.pyw` extension tells Windows to use `pythonw.exe`, which launches the application without creating a console window. Use `main.py` during development for debugging output.

## Running Tests

The project includes automated tests for checking scheduling algorithm behavior.

Run the test suite using:

```powershell
py -m unittest discover -s tests -v
```

The test suite helps verify scheduling logic and identify potential issues during development.

## Using the Application

### 1. Add a Process

Enter the following details in the sidebar:

- **PID:** Process identifier.
- **Arrival Time (AT):** Time at which the process enters the system (≥ 0).
- **Burst Time (BT):** CPU execution time required by the process (> 0).
- **Priority:** Priority assigned to the process (> 0, lower = higher priority).

Click **Add Process** to add the workload to the process table.

### 2. Manage Processes

Select a process from the table to:

- Edit its details.
- Delete the selected process.
- Clear the workload when required.

### 3. Configure Scheduling

Choose an algorithm from the available options.

- Set the time quantum for Round Robin (displayed only when Round Robin is selected).
- Select the required mode for Priority Scheduling.
- Review the configured workload before running the simulation.

### 4. Run a Simulation

Click **Run Simulation** to view:

- Process-level scheduling metrics.
- Aggregate performance metric cards.
- The execution timeline.
- A Matplotlib Gantt chart.

### 5. Compare Algorithms

Use the **Compare All Algorithms** button to run the current workload across all supported scheduling algorithms.

The comparison view allows you to examine differences in scheduling performance and select a specific algorithm's Gantt chart.

### 6. Reset Results

**Reset Results** clears the current simulation output without removing the existing process workload.

This allows you to run another algorithm using the same processes.

## Sample Workload

The following workload can be used to test the simulator.

| PID | Arrival Time (AT) | Burst Time (BT) | Priority |
|---|---:|---:|---:|
| P1 | 0 | 5 | 2 |
| P2 | 1 | 3 | 1 |
| P3 | 2 | 8 | 4 |
| P4 | 3 | 2 | 3 |
| P5 | 4 | 4 | 5 |

**Round Robin Time Quantum:** `2`

The simulator calculates completion times and other metrics from the execution timeline. Results should be verified against the generated timeline instead of relying on manually copied values.

## Project Structure

```text
.
├── main.py               # Development entry point
├── main.pyw              # Windows console-free entry point
├── models/
│   └── process.py        # Process data model
├── algorithms/
│   ├── common.py         # Shared scheduling utilities
│   ├── fcfs.py           # First Come First Serve
│   ├── sjf.py            # Shortest Job First
│   ├── srtf.py           # Shortest Remaining Time First
│   ├── round_robin.py    # Round Robin
│   └── priority.py       # Priority Scheduling
├── core/
│   ├── simulator.py      # Simulation dispatcher
│   └── metrics.py        # Metric calculations
├── gui/
│   ├── app.py            # Main application (Schedulix UI)
│   ├── gantt_chart.py    # Matplotlib Gantt chart
│   ├── process_table.py  # Input workload table
│   └── results_view.py   # Results table
├── tests/
│   ├── test_fcfs.py
│   ├── test_sjf.py
│   ├── test_srtf.py
│   ├── test_round_robin.py
│   └── test_priority.py
├── requirements.txt
└── README.md
```

### Directory Description

| Directory / File | Purpose |
|---|---|
| `main.py` | Application entry point (development). |
| `main.pyw` | Application entry point (Windows, no console). |
| `models/` | Contains process-related data models. |
| `algorithms/` | Contains individual CPU scheduling algorithm implementations. |
| `core/` | Handles simulation dispatching and metric calculations. |
| `gui/` | Contains CustomTkinter interfaces and Matplotlib chart components. |
| `tests/` | Contains automated tests for scheduling algorithms. |
| `requirements.txt` | Lists Python dependencies. |

## Learning Objectives

This project focuses on understanding the implementation and behavior of CPU scheduling algorithms.

Through this project, the following concepts are explored:

- Process scheduling and CPU allocation.
- Preemptive and non-preemptive scheduling.
- Arrival time, burst time, and priority handling.
- Waiting time, turnaround time, and response time.
- CPU idle time and execution timelines.
- Performance comparison between scheduling algorithms.
- GUI-based visualization of operating system concepts.

## Notes

- Priority 1 represents a higher priority than Priority 2.
- The simulator uses its defined tie-breaking rules when multiple processes are eligible.
- Scheduling results are calculated from the current workload and selected algorithm.
- Round Robin simulations require a valid time quantum.
- Resetting results does not remove the current workload.

## Developer

**Tamajit Modak**

## Academic Context

**Course:** Operating Systems

**Semester:** III

**Programme:** BCA (Hons.)

**University:** Parul University

**Faculty / Department:** FITCS

**Official Project Title:** CPU Scheduling Simulator

**Product Name:** Schedulix

## License

This project was developed for academic and learning purposes.

If you intend to share or reuse the project, add an appropriate license based on your requirements.
