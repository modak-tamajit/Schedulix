# Schedulix — Advanced CPU Scheduling Simulator

A modern desktop application designed for simulating, analyzing, and visualizing CPU scheduling algorithms in Operating Systems.

**Product Name:** Schedulix  
**Official Academic Project Title:** CPU Scheduling Simulator  
**Developer:** Tamajit Modak  
**Course:** Operating Systems — Semester III  
**Program:** BCA (Hons.)  
**Institution:** Parul University, Faculty of IT & Computer Science (FITCS)  
**Academic Year:** 2026–27  
**Technology Stack:** Python 3.10+, CustomTkinter, Matplotlib  

---

## 1. Project Overview

CPU scheduling is a fundamental operating system mechanism that determines how processes in the ready queue are allocated CPU time. Because different scheduling policies prioritize different optimization criteria—such as minimizing average waiting time, ensuring interactive responsiveness, or maximizing CPU utilization—practical exploration is critical for understanding their tradeoffs.

**Schedulix** transforms theoretical scheduling algorithms into an interactive, high-fidelity developer dashboard. Built with CustomTkinter and Matplotlib, it allows students, developers, and educators to configure workloads, execute scheduling simulations, inspect process execution timelines via Gantt charts, and evaluate six algorithm configurations side-by-side on identical workloads.

---

## 2. Key Features

- **Permanent Dark Developer Dashboard:** High-contrast palette (`#0D1117`, `#161B22`, `#1C2333`, `#6366F1`) adhering to modern developer-tool aesthetics with no distractions.
- **Interactive Algorithm Selection Cards:**
  - First Come First Serve (FCFS)
  - Round Robin (with dynamic inline Time Quantum entry)
  - Shortest Job First (with toggle between Non-preemptive SJF and Preemptive SRTF)
  - Priority Scheduling (with toggle between Non-preemptive and Preemptive modes)
- **Dual-View Navigation:**
  - **Single Algorithm Simulation:** Step-by-step workload management, simulation execution, individual process metrics, aggregate metrics cards, and Gantt chart.
  - **Algorithm Comparison:** Evaluates 6 algorithm configurations on the exact same workload, generating a comparative metrics table, a side-by-side grouped bar chart (Waiting Time vs. Turnaround Time), and a Gantt chart inspector.
- **Process Management Toolbar:**
  - **Add Process:** Validated input fields (Process ID, Arrival Time, Burst Time, Priority).
  - **Inline Editing (✎):** Load existing rows directly into the form for updates.
  - **Process Deletion (🗑):** Remove individual processes or clear all.
  - **Load Sample:** Instant 4-process quick demonstration workload.
  - **Export Workload:** Save workloads to `.json` or `.csv` files.
  - **Import Workload:** Load workloads from `.json` or `.csv` files with validation.
- **Verified Gantt Chart Visualization:** Embedded Matplotlib timeline with distinct curated process colors and clearly labeled idle intervals (`IDLE`).
- **Comprehensive Documentation & About Modals:** Quick reference for scheduling rules, tie-breaking criteria, standard metric equations, and academic attribution.

---

## 3. Supported Scheduling Algorithms

Schedulix supports five algorithm families evaluated across six explicit configurations:

| Algorithm Configuration | Classification | Queue Mechanism / Decision Rule | Preemption Behavior |
|---|---|---|---|
| **FCFS** | Non-preemptive | First-In, First-Out (FIFO) queue ordered by arrival time | Process runs to completion without interruption. |
| **SJF** | Non-preemptive | Selects available process with the shortest burst time | Process runs to completion; ties broken by arrival time, then input order. |
| **SRTF** | Preemptive | Selects available process with the shortest remaining execution time | Preempts current process if a newly arrived process has strictly shorter remaining time. Equal remaining time does not cause preemption. |
| **Round Robin (RR)** | Preemptive | Circular FIFO ready queue with fixed Time Quantum ($q$) | At quantum expiration, if other processes arrive at the exact boundary, newly arrived processes are queued before the preempted process. |
| **Priority (Non-preemptive)** | Non-preemptive | Selects available process with highest priority | Lower integer = higher priority ($1 > 2$). Runs to completion. |
| **Priority (Preemptive)** | Preemptive | Selects available process with highest priority | Preempts current process if an arriving process has strictly higher priority. |

### Tie-Breaking Hierarchy
When multiple candidate processes are equally eligible for CPU allocation, Schedulix resolves ties deterministically:
1. **Earlier Arrival Time:** Process that entered the ready queue earliest.
2. **Initial Input Order:** Order in which the process was defined in the workload.
3. **Lexicographical Process ID:** Alphabetic comparison of the PID string.

---

## 4. Scheduling Metrics & Mathematical Formulas

Schedulix computes process-level and aggregate metrics derived directly from operating system principles:

### Process-Level Metrics
- **Completion Time ($CT$):** The timestamp at which a process finishes its total execution.
- **Turnaround Time ($TAT$):** Total elapsed time from process arrival to its completion:
  $$\text{TAT} = \text{CT} - \text{AT}$$
- **Waiting Time ($WT$):** Total time spent by a process in the ready queue waiting for CPU allocation:
  $$\text{WT} = \text{TAT} - \text{BT}$$
- **Response Time ($RT$):** Time elapsed between process arrival and its very first CPU allocation:
  $$\text{RT} = \text{First CPU Start Time} - \text{AT}$$

### Aggregate Metrics
- **Average Waiting Time ($\overline{\text{WT}}$):**
  $$\overline{\text{WT}} = \frac{1}{n} \sum_{i=1}^{n} \text{WT}_i$$
- **Average Turnaround Time ($\overline{\text{TAT}}$):**
  $$\overline{\text{TAT}} = \frac{1}{n} \sum_{i=1}^{n} \text{TAT}_i$$
- **Average Response Time ($\overline{\text{RT}}$):**
  $$\overline{\text{RT}} = \frac{1}{n} \sum_{i=1}^{n} \text{RT}_i$$
- **CPU Utilization:** Percentage of total elapsed simulation time during which the CPU executed processes:
  $$\text{CPU Utilization} = \left(\frac{\text{Total Busy Time}}{\text{Total Simulation Time}}\right) \times 100$$
  *(Note: Idle intervals, including initial wait time before process arrival, are excluded from busy time).*
- **Throughput:** Number of processes completed per unit of simulation time:
  $$\text{Throughput} = \frac{n}{\text{Total Simulation Time}}$$

---

## 5. Workload Benchmarks & Verified Results

### A. Quick UI Demonstration Workload (4 Processes)
Used by the **Load Sample** button in the graphical interface:

| Process ID | Arrival Time ($AT$) | Burst Time ($BT$) | Priority |
|---|---|---|---|
| P1 | 0 | 5 | 2 |
| P2 | 1 | 3 | 1 |
| P3 | 2 | 8 | 3 |
| P4 | 3 | 6 | 1 |

#### Verified Results ($q = 2$):
| Algorithm Configuration | Avg Waiting Time ($\overline{\text{WT}}$) | Avg Turnaround Time ($\overline{\text{TAT}}$) | Avg Response Time ($\overline{\text{RT}}$) | CPU Utilization | Throughput |
|---|---|---|---|---|---|
| **FCFS** | 5.75 units | 11.25 units | 5.75 units | 100.00% | 0.182 p/u |
| **SJF** | 5.25 units | 10.75 units | 5.25 units | 100.00% | 0.182 p/u |
| **SRTF** | 5.00 units | 10.50 units | 4.25 units | 100.00% | 0.182 p/u |
| **Round Robin ($q=2$)** | 9.75 units | 15.25 units | 2.00 units | 100.00% | 0.182 p/u |
| **Priority (Non-preemptive)** | 5.25 units | 10.75 units | 5.25 units | 100.00% | 0.182 p/u |
| **Priority (Preemptive)** | 5.50 units | 11.00 units | 3.25 units | 100.00% | 0.182 p/u |

---

### B. Academic Benchmark Workload (5 Processes)
Standard academic benchmark documented in the accompanying [ACADEMIC_REPORT.md](file:///t:/Operating%20System/ACADEMIC_REPORT.md):

| Process ID | Arrival Time ($AT$) | Burst Time ($BT$) | Priority |
|---|---|---|---|
| P1 | 0 | 4 | 2 |
| P2 | 1 | 3 | 1 |
| P3 | 2 | 1 | 4 |
| P4 | 3 | 5 | 3 |
| P5 | 4 | 2 | 5 |

#### Verified Results ($q = 2$):
| Algorithm Configuration | Avg Waiting Time ($\overline{\text{WT}}$) | Avg Turnaround Time ($\overline{\text{TAT}}$) | Avg Response Time ($\overline{\text{RT}}$) | CPU Utilization | Throughput |
|---|---|---|---|---|---|
| **FCFS** | 4.40 units | 7.40 units | 4.40 units | 100.00% | 0.333 p/u |
| **SJF** | 3.20 units | 6.20 units | 3.20 units | 100.00% | 0.333 p/u |
| **SRTF** | 3.00 units | 6.00 units | 2.80 units | 100.00% | 0.333 p/u |
| **Round Robin ($q=2$)** | 5.00 units | 8.00 units | 2.40 units | 100.00% | 0.333 p/u |
| **Priority (Non-preemptive)** | 5.20 units | 8.20 units | 5.20 units | 100.00% | 0.333 p/u |
| **Priority (Preemptive)** | 5.20 units | 8.20 units | 4.60 units | 100.00% | 0.333 p/u |

---

## 6. Project Architecture & Directory Structure

```text
t:/Operating System/
├── algorithms/                 # Core scheduling algorithm implementations
│   ├── __init__.py             # Algorithm package exports
│   ├── common.py               # Shared queue and sorting helper routines
│   ├── fcfs.py                 # First Come First Serve
│   ├── priority.py             # Priority Scheduling (Preemptive & Non-preemptive)
│   ├── round_robin.py          # Round Robin with boundary arrival management
│   ├── sjf.py                  # Shortest Job First (Non-preemptive)
│   └── srtf.py                 # Shortest Remaining Time First (Preemptive)
├── core/                       # Core simulation engine and data management
│   ├── __init__.py
│   ├── data_io.py              # JSON & CSV workload import/export and benchmark sets
│   ├── metrics.py              # Mathematical metric calculations & Summary model
│   └── simulator.py            # Simulation coordinator and result builder
├── gui/                        # Desktop user interface (CustomTkinter & Matplotlib)
│   ├── __init__.py
│   ├── app.py                  # Main Schedulix window, navigation, and state
│   ├── comparison_chart.py     # Matplotlib grouped bar chart for comparison
│   ├── gantt_chart.py          # Matplotlib Gantt chart renderer
│   ├── process_table.py        # Process table style definitions
│   └── results_view.py         # Results treeview definitions
├── models/                     # Data models
│   ├── __init__.py
│   └── process.py              # Process dataclass and state tracking
├── tests/                      # Automated test suite
│   ├── __init__.py
│   ├── test_data_io.py         # Unit tests for JSON/CSV import/export
│   ├── test_fcfs.py            # Unit tests for FCFS logic and idle time
│   ├── test_metrics.py         # Unit tests for metric formulas against hand calculations
│   ├── test_priority.py        # Unit tests for priority modes and tie breaking
│   ├── test_round_robin.py     # Unit tests for RR quantum and arrival boundaries
│   ├── test_sjf.py             # Unit tests for shortest job selection
│   └── test_srtf.py            # Unit tests for preemption and remaining times
├── ACADEMIC_REPORT.md          # University coursework report with verified findings
├── README.md                   # Comprehensive project documentation
├── main.py                     # Application entry point
└── requirements.txt            # Project dependencies
```

---

## 7. Installation & Setup

### Prerequisites
- **Python 3.10+** installed on Windows, macOS, or Linux.
- `pip` package manager.

### Dependency Installation
Clone or navigate to the project directory and install requirements:
```bash
pip install -r requirements.txt
```

*(Contents of `requirements.txt`: `customtkinter>=5.2.0`, `matplotlib>=3.7.0`, `numpy>=1.24.0`)*

---

## 8. Running the Application

Launch the application using Python:
```bash
python main.py
```
*(On Windows, you can also run `pythonw main.py` if you prefer to launch the GUI window without a background terminal).*

---

## 9. Automated Testing

The project includes an automated test suite covering all scheduling algorithms, boundary behaviors, metric calculations, and data I/O.

Run all unit tests using Python's built-in test runner:
```bash
python -m unittest discover -s tests -v
```

All 16 unit tests execute in under 0.05 seconds with a 100% pass rate.

---

## 10. Academic Context & Attribution

This software was engineered as part of the academic curriculum for:
- **Course:** Operating Systems
- **Semester:** III
- **Program:** Bachelor of Computer Applications (Hons.)
- **Institution:** Parul University, Faculty of IT & Computer Science (FITCS)
- **Academic Year:** 2026–27
- **Developer:** Tamajit Modak
- **Repository:** [https://github.com/modak-tamajit/Schedulix](https://github.com/modak-tamajit/Schedulix)
