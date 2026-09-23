# Academic Project Report

# CPU Scheduling Simulator (Schedulix)
**An Interactive Simulation, Visualization, and Comparative Analysis System for Operating System Process Scheduling**

---

### Project & Academic Credentials

- **Official Project Title:** CPU Scheduling Simulator
- **Product & Application Name:** Schedulix
- **Student Name:** Tamajit Modak
- **Degree Program:** Bachelor of Computer Applications (Hons.) — BCA (Hons.)
- **Course Title:** Operating Systems (Semester III)
- **Academic Year:** 2026–27
- **Institution:** Parul University, Faculty of IT & Computer Science (FITCS), Vadodara, Gujarat
- **Faculty Guide / Supervisor:** Mrs. Priyanka Mod

---

## 1. Abstract

CPU scheduling is a foundational concept in multiprogramming and time-sharing operating systems, responsible for arbitrating the allocation of finite processor cores among concurrent processes. Because scheduling policies involve intricate tradeoffs between response time, fairness, throughput, and turnaround time, empirical observation through software simulation greatly enhances conceptual understanding.

This project presents **Schedulix**, a desktop CPU Scheduling Simulator developed using Python, CustomTkinter, and Matplotlib. Schedulix allows users to define process workloads, configure scheduling policies, execute deterministic simulations, inspect Gantt chart execution timelines with explicit idle intervals, and compare six distinct algorithm configurations on identical workloads. The system adheres to strict operating system scheduling conventions, incorporates robust input validation and JSON/CSV workload data I/O, and is validated by a 16-test automated verification suite.

---

## 2. Introduction & Problem Statement

In a modern operating system, the CPU is one of the most critical shared hardware resources. When multiple processes reside in the ready queue simultaneously, the kernel's CPU scheduler must choose which process executes next and for how long. The primary goals of CPU scheduling include:
1. **Maximizing CPU Utilization:** Ensuring the central processing unit is busy as much as possible.
2. **Maximizing Throughput:** Completing the highest possible number of processes per unit time.
3. **Minimizing Turnaround Time:** Reducing the total elapsed time between process arrival and completion.
4. **Minimizing Waiting Time:** Reducing the cumulative duration a process spends idle in the ready queue.
5. **Minimizing Response Time:** Reducing the latency before a process first starts executing on the CPU (critical for interactive systems).

Manually solving CPU scheduling problems using pen and paper for complex process sets is error-prone, particularly when handling preemptive interrupts, zero-burst transitions, and time-quantum boundary arrivals. Schedulix was engineered to provide an interactive, automated, and mathematically verified laboratory platform for OS scheduling analysis.

---

## 3. Supported Scheduling Algorithms & Theoretical Foundations

Schedulix implements five core scheduling algorithm families evaluated across six operational configurations:

### 3.1 First Come First Serve (FCFS)
- **Nature:** Non-preemptive.
- **Principle:** Processes are executed in the exact order of their arrival into the ready queue (FIFO discipline).
- **Characteristics:** Simple to implement with zero scheduling overhead. However, it suffers from the **Convoy Effect**, where short processes are forced to wait behind long CPU-bound processes, leading to elevated average waiting times.

### 3.2 Shortest Job First (SJF)
- **Nature:** Non-preemptive.
- **Principle:** When the CPU becomes free, the scheduler selects the eligible process with the shortest initial CPU burst time.
- **Characteristics:** Proven to be provably optimal for minimizing average waiting time among non-preemptive algorithms for a fixed set of processes. Its practical limitation in production operating systems is the inability to know exact future burst times in advance.

### 3.3 Shortest Remaining Time First (SRTF)
- **Nature:** Preemptive counterpart to SJF.
- **Principle:** At any point in time, if a newly arriving process has a remaining burst time strictly less than the remaining burst time of the currently executing process, the CPU preempts the running process and switches to the new process.
- **Tie-Breaking Rule:** If an arriving process has an identical remaining burst time to the running process, preemption does **not** occur (`test_equal_remaining_does_not_fake_switch`), preventing unnecessary context-switch overhead.

### 3.4 Round Robin (RR)
- **Nature:** Preemptive time-slicing.
- **Principle:** The CPU ready queue is treated as a circular FIFO queue. Each process is allocated a discrete slice of CPU time called a **Time Quantum** ($q$). If the process does not complete within its quantum, it is preempted and requeued at the tail of the ready queue.
- **Boundary Arrival Management:** In Schedulix, when a process's quantum expires at time $t$ exactly as another process arrives at time $t$, the newly arriving process is enqueued into the ready queue **before** the expired process is re-added, ensuring strict chronological fairness.

### 3.5 Priority Scheduling (Non-preemptive & Preemptive)
- **Nature:** Supports both Preemptive and Non-preemptive execution.
- **Principle:** Each process is assigned an integer priority value.
- **Priority Convention:** In Schedulix, a **lower numerical value represents a higher priority** (e.g., Priority $1$ has precedence over Priority $2$).
- **Non-preemptive Mode:** Once the CPU is allocated to a process, it holds the CPU until completion.
- **Preemptive Mode:** If a newly arrived process possesses a strictly higher priority (lower integer value) than the currently running process, the running process is immediately preempted.

### 3.6 Deterministic Tie-Breaking Protocol
To ensure reproducible, deterministic scheduling behavior across all algorithms:
1. **Primary criterion:** Algorithm decision rule (arrival time, burst time, remaining time, or priority).
2. **Secondary criterion:** Earlier arrival time ($AT$).
3. **Tertiary criterion:** Original input sequence index.
4. **Quaternary criterion:** Lexicographical Process ID comparison ($PID$).

---

## 4. Mathematical Formulations of Scheduling Metrics

Let $P_i$ denote a process with Arrival Time $AT_i$ and Burst Time $BT_i$. The simulator calculates:

1. **Completion Time ($CT_i$):**
   Timestamp at which $P_i$ terminates execution.

2. **Turnaround Time ($TAT_i$):**
   $$\text{TAT}_i = \text{CT}_i - \text{AT}_i$$

3. **Waiting Time ($WT_i$):**
   $$\text{WT}_i = \text{TAT}_i - \text{BT}_i$$

4. **Response Time ($RT_i$):**
   $$\text{RT}_i = \text{First CPU Start Time}_i - \text{AT}_i$$

5. **Average Waiting Time ($\overline{\text{WT}}$):**
   $$\overline{\text{WT}} = \frac{1}{n} \sum_{i=1}^{n} \text{WT}_i \quad (\text{time units})$$

6. **Average Turnaround Time ($\overline{\text{TAT}}$):**
   $$\overline{\text{TAT}} = \frac{1}{n} \sum_{i=1}^{n} \text{TAT}_i \quad (\text{time units})$$

7. **Average Response Time ($\overline{\text{RT}}$):**
   $$\overline{\text{RT}} = \frac{1}{n} \sum_{i=1}^{n} \text{RT}_i \quad (\text{time units})$$

8. **CPU Utilization (%):**
   $$\text{CPU Utilization} = \left(\frac{\text{Total Busy Time}}{\text{Total Elapsed Time}}\right) \times 100$$
   where $\text{Total Elapsed Time} = \max(CT)$, clock begins at $0$, and intervals labeled `IDLE` are subtracted from busy time.

9. **Throughput:**
   $$\text{Throughput} = \frac{n}{\text{Total Elapsed Time}} \quad (\text{processes / time unit})$$

---

## 5. Experimental Evaluation on Academic Benchmark Workload

To empirically evaluate the behavior of all six algorithm configurations, the following verified 5-process benchmark workload was executed through Schedulix:

### 5.1 Benchmark Input Workload

| Process ID | Arrival Time ($AT$) | Burst Time ($BT$) | Priority |
|---|---|---|---|
| **P1** | 0 | 4 | 2 |
| **P2** | 1 | 3 | 1 |
| **P3** | 2 | 1 | 4 |
| **P4** | 3 | 5 | 3 |
| **P5** | 4 | 2 | 5 |

Total Burst Requirement: $\sum BT = 4 + 3 + 1 + 5 + 2 = 15$ time units.

---

### 5.2 Algorithm Execution Details & Gantt Timelines

#### Configuration 1: FCFS (Non-preemptive)
- **Execution Order:** P1 $[0 \to 4]$, P2 $[4 \to 7]$, P3 $[7 \to 8]$, P4 $[8 \to 13]$, P5 $[13 \to 15]$
- **Process Metrics:**
  - P1: $CT = 4, TAT = 4, WT = 0, RT = 0$
  - P2: $CT = 7, TAT = 6, WT = 3, RT = 3$
  - P3: $CT = 8, TAT = 6, WT = 5, RT = 5$
  - P4: $CT = 13, TAT = 10, WT = 5, RT = 5$
  - P5: $CT = 15, TAT = 11, WT = 9, RT = 9$
- **Summary:** $\overline{WT} = 4.40\text{ units}$, $\overline{TAT} = 7.40\text{ units}$, $\overline{RT} = 4.40\text{ units}$, CPU Util = $100.00\%$, Throughput = $0.333$

#### Configuration 2: SJF (Non-preemptive)
- **Execution Order:** P1 $[0 \to 4]$, P3 $[4 \to 5]$, P5 $[5 \to 7]$, P2 $[7 \to 10]$, P4 $[10 \to 15]$
- **Process Metrics:**
  - P1: $CT = 4, TAT = 4, WT = 0, RT = 0$
  - P2: $CT = 10, TAT = 9, WT = 6, RT = 6$
  - P3: $CT = 5, TAT = 3, WT = 2, RT = 2$
  - P4: $CT = 15, TAT = 12, WT = 7, RT = 7$
  - P5: $CT = 7, TAT = 3, WT = 1, RT = 1$
- **Summary:** $\overline{WT} = 3.20\text{ units}$, $\overline{TAT} = 6.20\text{ units}$, $\overline{RT} = 3.20\text{ units}$, CPU Util = $100.00\%$, Throughput = $0.333$

#### Configuration 3: SRTF (Preemptive SJF)
- **Execution Order:** P1 $[0 \to 2]$, P3 $[2 \to 3]$, P1 $[3 \to 5]$, P5 $[5 \to 7]$, P2 $[7 \to 10]$, P4 $[10 \to 15]$
- **Process Metrics:**
  - P1: $CT = 5, TAT = 5, WT = 1, RT = 0$
  - P2: $CT = 10, TAT = 9, WT = 6, RT = 6$
  - P3: $CT = 3, TAT = 1, WT = 0, RT = 0$
  - P4: $CT = 15, TAT = 12, WT = 7, RT = 7$
  - P5: $CT = 7, TAT = 3, WT = 1, RT = 1$
- **Summary:** $\overline{WT} = 3.00\text{ units}$, $\overline{TAT} = 6.00\text{ units}$, $\overline{RT} = 2.80\text{ units}$, CPU Util = $100.00\%$, Throughput = $0.333$

> [!NOTE]
> **Detailed Mathematical & Algorithmic Analysis of SRTF Response Time ($2.80$ vs. $1.60$ time units):**
> 1. **At $t=0$:** P1 starts executing ($First Start = 0 \implies RT = 0$).
> 2. **At $t=1$:** P1 has executed for 1 time unit; its remaining burst is $4 - 1 = 3$. Process P2 arrives with burst time $3$. Because P2's remaining time ($3$) is equal to—not strictly less than—P1's remaining burst ($3$), and P1 arrived earlier ($AT=0 < AT=1$), P1 is **not** preempted. Schedulix strictly enforces this rule (`test_equal_remaining_does_not_fake_switch`) to prevent wasteful, unnecessary context switches when no progress advantage exists.
> 3. **At $t=2$:** P1 has executed for another unit (remaining $= 2$). Process P3 arrives with burst $= 1$. Because $1 < 2$, P3 strictly preempts P1 and executes from $[2 \to 3]$.
> 4. **At $t=3$:** P3 terminates ($CT=3, RT=0$). Ready queue candidates are: P1 (remaining $= 2$), P2 (remaining $= 3$), P4 (remaining $= 5$). P1 has the minimum remaining burst ($2 < 3$), so P1 resumes from $[3 \to 5]$ and terminates ($CT=5$).
> 5. **At $t=5$:** P5 (arrived at $t=4$ with burst $= 2$) has remaining time $2 < 3$ compared to P2. P5 executes from $[5 \to 7]$ and terminates ($CT=7, RT = 5 - 4 = 1$).
> 6. **At $t=7$:** Process P2 finally receives its very first CPU allocation. Since $AT=1$, P2's Response Time is $7 - 1 = 6$ time units.
> 7. **At $t=10$:** Process P4 receives its first CPU allocation ($RT = 10 - 3 = 7$) and executes to $t=15$.
>
> Therefore, the exact individual response times are:
> $$\sum RT = RT(P1) + RT(P2) + RT(P3) + RT(P4) + RT(P5) = 0 + 6 + 0 + 7 + 1 = 14$$
> $$\overline{\text{RT}} = \frac{14}{5} = \mathbf{2.80\text{ time units}}$$
>
> *(Note on alternate models: If an implementation had allowed equal remaining times to preempt the running process at $t=1$, P2 would have started at $t=1$ with $RT=0$, which would yield an average RT of $1.60$. However, in standard operating system scheduling theory and the Schedulix test suite, equal remaining time does not trigger preemption, verifying $\overline{RT} = 2.80$).*

#### Configuration 4: Round Robin ($q = 2$)
- **Execution Order:** P1 $[0 \to 2]$, P2 $[2 \to 4]$, P3 $[4 \to 5]$, P1 $[5 \to 7]$, P4 $[7 \to 9]$, P5 $[9 \to 11]$, P2 $[11 \to 12]$, P4 $[12 \to 14]$, P4 $[14 \to 15]$
- **Process Metrics:**
  - P1: $CT = 7, TAT = 7, WT = 3, RT = 0$
  - P2: $CT = 12, TAT = 11, WT = 8, RT = 1$
  - P3: $CT = 5, TAT = 3, WT = 2, RT = 2$
  - P4: $CT = 15, TAT = 12, WT = 7, RT = 4$
  - P5: $CT = 11, TAT = 7, WT = 5, RT = 5$
- **Summary:** $\overline{WT} = 5.00\text{ units}$, $\overline{TAT} = 8.00\text{ units}$, $\overline{RT} = 2.40\text{ units}$, CPU Util = $100.00\%$, Throughput = $0.333$

#### Configuration 5: Priority (Non-preemptive)
- **Execution Order:** P1 $[0 \to 4]$, P2 $[4 \to 7]$, P4 $[7 \to 12]$, P3 $[12 \to 13]$, P5 $[13 \to 15]$
- **Process Metrics:**
  - P1: $CT = 4, TAT = 4, WT = 0, RT = 0$
  - P2: $CT = 7, TAT = 6, WT = 3, RT = 3$
  - P3: $CT = 13, TAT = 11, WT = 10, RT = 10$
  - P4: $CT = 12, TAT = 9, WT = 4, RT = 4$
  - P5: $CT = 15, TAT = 11, WT = 9, RT = 9$
- **Summary:** $\overline{WT} = 5.20\text{ units}$, $\overline{TAT} = 8.20\text{ units}$, $\overline{RT} = 5.20\text{ units}$, CPU Util = $100.00\%$, Throughput = $0.333$

#### Configuration 6: Priority (Preemptive)
- **Execution Order:** P1 $[0 \to 1]$, P2 $[1 \to 4]$, P1 $[4 \to 7]$, P4 $[7 \to 12]$, P3 $[12 \to 13]$, P5 $[13 \to 15]$
  *(Note: At time 1, P2 arrives with Priority 1, which is strictly higher than P1's Priority 2. P1 is preempted).*
- **Process Metrics:**
  - P1: $CT = 7, TAT = 7, WT = 3, RT = 0$
  - P2: $CT = 4, TAT = 3, WT = 0, RT = 0$
  - P3: $CT = 13, TAT = 11, WT = 10, RT = 10$
  - P4: $CT = 12, TAT = 9, WT = 4, RT = 4$
  - P5: $CT = 15, TAT = 11, WT = 9, RT = 9$
- **Summary:** $\overline{WT} = 5.20\text{ units}$, $\overline{TAT} = 8.20\text{ units}$, $\overline{RT} = 4.60\text{ units}$, CPU Util = $100.00\%$, Throughput = $0.333$

---

### 5.3 Comparative Performance Matrix

| Algorithm Configuration | $\overline{\text{WT}}$ (units) | $\overline{\text{TAT}}$ (units) | $\overline{\text{RT}}$ (units) | CPU Utilization | Throughput (proc/unit) | Total Time |
|---|---|---|---|---|---|---|
| **FCFS** | 4.40 | 7.40 | 4.40 | 100.00% | 0.333 | 15 |
| **SJF (Non-preemptive)** | 3.20 | 6.20 | 3.20 | 100.00% | 0.333 | 15 |
| **SRTF (Preemptive SJF)** | **3.00** | **6.00** | 2.80 | 100.00% | 0.333 | 15 |
| **Round Robin ($q=2$)** | 5.00 | 8.00 | **2.40** | 100.00% | 0.333 | 15 |
| **Priority (Non-preemptive)** | 5.20 | 8.20 | 5.20 | 100.00% | 0.333 | 15 |
| **Priority (Preemptive)** | 5.20 | 8.20 | 4.60 | 100.00% | 0.333 | 15 |

---

### 5.4 Analytical Observations on the Benchmark Workload

1. **Optimal Waiting Time for Workload:** On this benchmark workload, **SRTF** achieved the lowest average waiting time ($3.00$ time units) and turnaround time ($6.00$ time units). By preempting P1 at time $t=2$ to execute the 1-unit burst of P3, SRTF prevented P3 from queuing behind larger jobs.
2. **Interactive Responsiveness:** **Round Robin ($q=2$)** yielded the lowest average response time ($2.40$ time units), demonstrating its suitability for interactive systems where early responsiveness is prioritized over minimizing cumulative turnaround.
3. **Preemption Impact on Priority Scheduling:** Preemptive Priority scheduling reduced the average response time from $5.20$ to $4.60$ time units compared to Non-preemptive Priority, because P2 (Priority 1) received immediate CPU allocation upon arrival at $t=1$.
4. **Academic Caution:** In operating system theory, **no single scheduling algorithm is universally superior across all workloads**. While SRTF minimized turnaround time for this batch mix, in real-time or time-shared systems, Round Robin or Multi-Level Feedback Queues are preferred to prevent starvation of long jobs.

---

## 6. Software Architecture & Implementation Details

Schedulix is structured into clean modular layers following separation-of-concerns principles:

- **`models/process.py`:** Contains the `Process` dataclass, encapsulating state variables ($AT, BT, Priority$, remaining time, start time, completion time, order).
- **`algorithms/`:** Pure algorithmic scheduling modules with no graphical dependencies, facilitating automated unit testing and headless validation.
- **`core/simulator.py`:** High-level coordinator that creates isolated copies of process workloads, dispatches to algorithm engines, records execution segments, and triggers metrics generation.
- **`core/data_io.py`:** File I/O handling JSON/CSV export and import with attribute validation and error management.
- **`gui/app.py`:** Desktop interface engineered with CustomTkinter, managing dual navigation tabs, interactive algorithm cards, inline CRUD tables, and modal dialogs.
- **`gui/gantt_chart.py` & `gui/comparison_chart.py`:** Matplotlib integration rendering dark-themed timeline bars and comparative performance bar charts.

---

## 7. Verification & Automated Test Suite

The implemented test suite completed successfully with 16 passing tests during the final verification run:
- `test_fcfs.py`: Validates arrival ordering, idle interval insertion, and single-process handling.
- `test_sjf.py`: Validates non-preemptive shortest job selection and tie-breaking.
- `test_srtf.py`: Validates preemptive switching on shorter remaining time and verifies that equal remaining time does not cause erroneous context switches.
- `test_round_robin.py`: Validates multi-cycle quantum round robin, quantum boundary arrivals, and invalid quantum detection.
- `test_priority.py`: Validates preemptive and non-preemptive priority hierarchies and tie resolution.
- `test_metrics.py`: Validates $TAT, WT, RT$, CPU Utilization, and Throughput calculations against hand-solved ground truth.
- `test_data_io.py`: Validates JSON and CSV export, import, structure validation, and sample workload retrieval.

**Test Run Result:**
```text
Ran 16 tests in 0.013s — OK (100% Passing)
```

---

## 8. Conclusion & Future Scope

### 8.1 Conclusion
The **Schedulix** CPU Scheduling Simulator successfully demonstrates the theoretical concepts and mathematical tradeoffs of operating system process scheduling within a robust, professional software framework. By combining high-fidelity dark UI aesthetics with mathematically verified simulation algorithms and automated testing, the project provides a comprehensive, academically sound tool for computer science students and educators.

### 8.2 Future Scope
Potential extensions for future iterations include:
- Implementation of **Multi-Level Queue (MLQ)** and **Multi-Level Feedback Queue (MLFQ)** scheduling.
- Support for **I/O burst cycles** alternating with CPU bursts.
- Real-time simulation speed throttling with step-by-step queue animation.
- Simulation of multi-core / symmetric multiprocessing (SMP) load balancing.

---

**Report Submission Signature:**  
*Tamajit Modak*  
BCA (Hons.), Semester III  
Parul University, FITCS  
Academic Year 2026–27
