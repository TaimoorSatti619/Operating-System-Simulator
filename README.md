# Operating System CPU Scheduling Simulator

A Python-based interactive application built with **Streamlit** to demonstrate and simulate different CPU scheduling algorithms used in Operating Systems.

The application allows users to select a scheduling algorithm, provide process information, and understand how the CPU allocates time to different processes. It helps students learn scheduling concepts through examples, execution results, and scheduling timelines.

## Table of Contents

1. Project Overview
2. Objectives
3. Technologies Used
4. CPU Scheduling Basics
5. Scheduling Algorithms
   - First Come First Serve (FCFS)
   - Shortest Job First (SJF)
   - Shortest Remaining Time First (SRTF)
   - Priority Scheduling
   - Round Robin (RR)
   - Multilevel Queue (MLQ)
   - Multilevel Feedback Queue (MLFQ)
6. Scheduling Formulas
7. Example of Scheduling Calculations
8. Preemptive vs Non-Preemptive Scheduling
9. Installation and Execution
10. Project Structure
11. Input Parameters
12. Advantages and Limitations
13. Future Improvements
14. Conclusion

---

## 1. Project Overview

CPU scheduling is an important function of an Operating System. When multiple processes are ready to execute, the operating system decides which process should use the CPU and for how long.

This project provides an interactive way to understand CPU scheduling algorithms without manually calculating every result.

Users can select an algorithm, enter process details such as arrival time, burst time, and priority, and observe the resulting execution order and scheduling calculations.

## 2. Objectives

The main objectives of this project are:

- To understand the working of CPU scheduling algorithms.
- To compare preemptive and non-preemptive scheduling.
- To calculate completion, turnaround, waiting, and response times.
- To visualize the order in which processes execute.
- To demonstrate how different algorithms affect process waiting times.
- To provide a simple educational tool for Operating Systems students.

## 3. Technologies Used

- **Python:** Implements the scheduling algorithms and calculations.
- **Streamlit:** Creates the interactive web application.
- **Pandas:** Can be used to display process information and results in tables.
- **Matplotlib or other visualization libraries:** Can be used if included in the project for scheduling charts.

## 4. CPU Scheduling Basics

A process is a program that is currently being executed by an operating system.

Each process may have the following information:

| Term | Meaning |
|---|---|
| Process ID (PID) | Unique identifier of a process |
| Arrival Time (AT) | Time when a process enters the ready queue |
| Burst Time (BT) | Total CPU time required by a process |
| Completion Time (CT) | Time when a process finishes execution |
| Turnaround Time (TAT) | Total time spent in the system |
| Waiting Time (WT) | Time spent waiting for CPU execution |
| Response Time (RT) | Time from arrival until the process first receives the CPU |
| Priority | Value used to determine scheduling preference |
| Time Quantum | Maximum CPU time allocated in one Round Robin turn |

### Example

Suppose Process P1 arrives at time 0 and requires 5 units of CPU time.

- PID: P1
- Arrival Time: 0
- Burst Time: 5

If P1 executes continuously from time 0 to time 5, its completion time is 5.

Its turnaround time is:

`TAT = CT - AT = 5 - 0 = 5`

Its waiting time is:

`WT = TAT - BT = 5 - 5 = 0`

Therefore, P1 finishes without waiting.

---

## 5. Scheduling Algorithms

### 5.1 First Come First Serve (FCFS)

**Type:** Non-preemptive

FCFS executes processes in the order they arrive in the ready queue. The process that arrives first gets the CPU first.

Once a process starts executing, it continues until it finishes.

#### Example

Assume all processes arrive at time 0.

| Process | Arrival Time | Burst Time |
|---|---:|---:|
| P1 | 0 | 5 |
| P2 | 0 | 3 |
| P3 | 0 | 2 |

Execution order:

`P1 → P2 → P3`

Gantt chart:

```text
0       5       8      10
|  P1   |  P2   |  P3  |
```

Calculations:

| Process | CT | TAT = CT - AT | WT = TAT - BT |
|---|---:|---:|---:|
| P1 | 5 | 5 | 0 |
| P2 | 8 | 8 | 5 |
| P3 | 10 | 10 | 8 |

Average waiting time:

`(0 + 5 + 8) / 3 = 4.33`

#### Advantages

- Simple to understand and implement.
- Fair according to arrival order.
- No process is deliberately skipped in favor of a later arrival.

#### Disadvantages

- A long process can make shorter processes wait.
- Can cause the convoy effect, where several short processes wait behind a long one.

---

### 5.2 Shortest Job First (SJF)

**Type:** Non-preemptive

Shortest Job First selects the process with the smallest burst time from the processes that have already arrived and are ready.

After execution begins, the selected process continues until completion.

#### Example

Assume all processes arrive at time 0.

| Process | Arrival Time | Burst Time |
|---|---:|---:|
| P1 | 0 | 5 |
| P2 | 0 | 3 |
| P3 | 0 | 2 |

The shortest burst time is P3, followed by P2 and then P1.

Execution order:

`P3 → P2 → P1`

Gantt chart:

```text
0      2       5          10
|  P3  |  P2   |    P1    |
```

Calculations:

| Process | CT | TAT | WT |
|---|---:|---:|---:|
| P1 | 10 | 10 | 5 |
| P2 | 5 | 5 | 2 |
| P3 | 2 | 2 | 0 |

Average waiting time:

`(5 + 2 + 0) / 3 = 2.33`

In this example, SJF has a lower average waiting time than FCFS.

#### Advantages

- Often reduces average waiting time.
- Short processes can finish quickly.

#### Disadvantages

- Long processes may suffer from starvation.
- The operating system may not know the actual CPU burst time in advance.

**Important:** This project's standard SJF uses the burst times supplied as input. SJF based on predicted future CPU bursts is a related concept, but it requires a prediction mechanism to be implemented separately.

#### Predicting the Next CPU Burst

An operating system can estimate a future CPU burst using exponential averaging:

`τ(n+1) = α × t(n) + (1 - α) × τ(n)`

Where:

- `τ(n+1)` is the predicted next CPU burst.
- `t(n)` is the most recently observed actual burst.
- `τ(n)` is the previous prediction.
- `α` is a value between 0 and 1.

For example, if the previous prediction is 6, the latest actual burst is 4, and α = 0.5:

`τ(n+1) = 0.5 × 4 + 0.5 × 6 = 5`

The next predicted burst is 5 time units.

---

### 5.3 Shortest Remaining Time First (SRTF)

**Type:** Preemptive

SRTF is the preemptive version of Shortest Job First.

At any moment, the CPU executes the ready process with the smallest remaining burst time. If a new process arrives with a shorter remaining time than the currently running process, the CPU can switch to the new process.

#### Example

| Process | Arrival Time | Burst Time |
|---|---:|---:|
| P1 | 0 | 7 |
| P2 | 2 | 4 |
| P3 | 4 | 1 |

Working:

1. At time 0, P1 starts.
2. At time 2, P2 arrives. P1 has 5 units remaining, while P2 needs 4, so P2 runs.
3. At time 4, P3 arrives. P2 has 2 units remaining, so P2 continues.
4. P2 finishes at time 6.
5. P3 runs from time 6 to 7.
6. P1 resumes and finishes at time 12.

Gantt chart:

```text
0       2           6   7             12
|  P1   |    P2     | P3 |     P1      |
```

Calculations:

| Process | CT | TAT | WT |
|---|---:|---:|---:|
| P1 | 12 | 12 | 5 |
| P2 | 6 | 4 | 0 |
| P3 | 7 | 3 | 2 |

Average waiting time:

`(5 + 0 + 2) / 3 = 2.33`

#### Advantages

- Short remaining jobs can finish sooner.
- Can reduce average waiting time.

#### Disadvantages

- Processes may be interrupted multiple times.
- Long processes can experience starvation.
- More scheduling decisions are required than with non-preemptive SJF.

---

### 5.4 Priority Scheduling

**Type:** Preemptive or non-preemptive, depending on the selected version.

Priority Scheduling chooses a process according to its priority value.

For this project's examples, **a smaller priority number means a higher priority**. For example, priority 1 is higher than priority 3.

#### Example

Assume all processes arrive at time 0 and use non-preemptive Priority Scheduling.

| Process | Burst Time | Priority |
|---|---:|---:|
| P1 | 4 | 3 |
| P2 | 3 | 1 |
| P3 | 2 | 2 |

Execution order:

`P2 → P3 → P1`

Gantt chart:

```text
0       3      5         9
|  P2   |  P3  |   P1    |
```

Calculations:

| Process | CT | TAT | WT |
|---|---:|---:|---:|
| P1 | 9 | 9 | 5 |
| P2 | 3 | 3 | 0 |
| P3 | 5 | 5 | 3 |

Average waiting time:

`(5 + 0 + 3) / 3 = 2.67`

#### Preemptive Priority Scheduling

In the preemptive version, a newly arrived process can interrupt the current process if its priority is higher.

In the non-preemptive version, the running process continues until it completes.

#### Advantages

- Important or urgent processes can be executed first.
- Useful when processes have different levels of importance.

#### Disadvantages

- Low-priority processes may starve.
- A common solution to starvation is aging, which gradually increases the priority of waiting processes. Aging is not necessarily implemented in this simulator.

---

### 5.5 Round Robin (RR)

**Type:** Preemptive

Round Robin is designed to share CPU time among processes fairly.

Each ready process receives the CPU for a fixed period called the **time quantum**. If the process does not finish within that period, it is interrupted and placed at the end of the ready queue.

#### Example

Assume all processes arrive at time 0 and the time quantum is 2.

| Process | Burst Time |
|---|---:|
| P1 | 5 |
| P2 | 3 |
| P3 | 1 |

Initial ready queue:

`P1 → P2 → P3`

Execution:

1. P1 runs for 2 units. Remaining burst = 3.
2. P2 runs for 2 units. Remaining burst = 1.
3. P3 runs for 1 unit and finishes.
4. P1 runs for 2 more units. Remaining burst = 1.
5. P2 runs for 1 unit and finishes.
6. P1 runs for its final 1 unit and finishes.

Gantt chart:

```text
0     2     4   5     7   8   9
| P1  | P2  |P3 | P1  |P2 |P1 |
```

Calculations:

| Process | CT | TAT | WT |
|---|---:|---:|---:|
| P1 | 9 | 9 | 4 |
| P2 | 8 | 8 | 5 |
| P3 | 5 | 5 | 4 |

Average waiting time:

`(4 + 5 + 4) / 3 = 4.33`

#### Advantages

- Gives processes regular opportunities to use the CPU.
- Suitable for time-sharing systems.
- Prevents one process from keeping the CPU indefinitely.

#### Disadvantages

- A very small quantum causes frequent context switches.
- A very large quantum makes the algorithm behave more like FCFS.
- Performance depends on choosing a suitable quantum.

---

### 5.6 Multilevel Queue Scheduling (MLQ)

**Type:** Depends on the queue-selection policy; this project's implementation uses higher-priority queues that can preempt lower-priority queues.

Multilevel Queue Scheduling divides the ready queue into multiple separate queues. Each queue may represent a different category of processes.

For example:

- Queue 1: High-priority processes
- Queue 2: Medium-priority processes
- Queue 3: Low-priority processes

In this project's implementation, lower queue numbers indicate higher priority. A process in a higher-priority queue can interrupt a process running in a lower-priority queue.

Within a queue, processes are handled according to the implementation's queue policy.

#### Example

Assume:

| Process | Arrival Time | Burst Time | Queue |
|---|---:|---:|---:|
| P1 | 0 | 5 | 2 |
| P2 | 1 | 2 | 1 |
| P3 | 0 | 3 | 3 |

Queue 1 has the highest priority, followed by Queue 2 and Queue 3.

Working:

1. At time 0, P1 begins execution from Queue 2.
2. P3 belongs to Queue 3, so P1 has higher priority.
3. At time 1, P2 arrives in Queue 1 and interrupts P1.
4. P2 runs from time 1 to 3 and finishes.
5. P1 resumes and finishes at time 7.
6. P3 then runs from time 7 to 10.

Gantt chart:

```text
0   1       3           7          10
|P1 |  P2   |     P1    |    P3    |
```

#### Advantages

- Separates processes into meaningful categories.
- Different queues can use different scheduling policies.
- Higher-priority categories can receive faster CPU access.

#### Disadvantages

- Low-priority queues may experience starvation.
- Processes are generally assigned to a particular queue.
- Queue assignment and priority policies affect overall performance.

**Note:** This example assumes the same fixed-queue priority behavior as the project's implementation. Queue policies can differ in other MLQ systems.

---

### 5.7 Multilevel Feedback Queue Scheduling (MLFQ)

**Type:** Preemptive

Multilevel Feedback Queue Scheduling also uses multiple queues, but it allows processes to move between them.

New processes normally enter the highest-priority queue. If a process uses its full time quantum without finishing, it may be moved to a lower-priority queue.

A process in a higher-priority queue can interrupt a process in a lower-priority queue when it becomes ready.

This project uses example queue quantums of 2, 4, and 8 time units by default.

#### Example

Assume one process P1 arrives at time 0 and requires 9 units of CPU time.

| Queue | Time Quantum | Execution |
|---|---:|---|
| Q1 | 2 | P1 runs for 2 units |
| Q2 | 4 | P1 runs for 4 units |
| Q3 | 8 | P1 runs for the remaining 3 units |

Working:

1. P1 enters Q1 and runs from time 0 to 2.
2. P1 still has 7 units remaining, so it is demoted to Q2.
3. P1 runs from time 2 to 6 in Q2.
4. P1 still has 3 units remaining, so it is demoted to Q3.
5. P1 runs from time 6 to 9 and finishes.

Gantt chart:

```text
0       2               6       9
|  Q1   |       Q2      |  Q3   |
```

Completion time = 9

Turnaround time = 9 - 0 = 9

Waiting time = 9 - 9 = 0

#### Advantages

- Adapts scheduling to process behavior.
- Short or interactive jobs can receive fast service.
- Long CPU-intensive jobs can move to lower queues.
- More flexible than ordinary Multilevel Queue Scheduling.

#### Disadvantages

- More complex to implement.
- Results depend on the number of queues and their time quantums.
- Long processes may wait too long if high-priority processes keep arriving.

**Implementation note:** This project's MLFQ uses the configured quantums and demotes unfinished processes when they consume their full quantum. It does not implement aging or periodic promotion unless additional logic is added.

---

## 6. Scheduling Formulas

These formulas are used to evaluate scheduling results.

### Completion Time (CT)

The time at which a process finishes its execution.

### Turnaround Time (TAT)

Total time between process arrival and completion.

`TAT = CT - AT`

### Waiting Time (WT)

Total time a process spends waiting in the ready queue.

`WT = TAT - BT`

### Response Time (RT)

Time between process arrival and its first CPU execution.

`RT = First CPU Start Time - AT`

### Average Waiting Time

`Average WT = Sum of all Waiting Times / Number of Processes`

### Average Turnaround Time

`Average TAT = Sum of all Turnaround Times / Number of Processes`

### Average Response Time

`Average RT = Sum of all Response Times / Number of Processes`

### CPU Utilization

When idle time is tracked, CPU utilization can be calculated as:

`CPU Utilization = (CPU Busy Time / Total Elapsed Time) × 100`

The exact metrics displayed depend on what the current application calculates and shows.

---

## 7. Example of Scheduling Calculations

Consider these processes using FCFS:

| Process | Arrival Time | Burst Time |
|---|---:|---:|
| P1 | 0 | 4 |
| P2 | 1 | 3 |
| P3 | 2 | 2 |

Execution:

```text
0       4       7     9
|  P1   |  P2   | P3  |
```

### Process P1

- CT = 4
- TAT = 4 - 0 = 4
- WT = 4 - 4 = 0
- RT = 0 - 0 = 0

### Process P2

- CT = 7
- TAT = 7 - 1 = 6
- WT = 6 - 3 = 3
- RT = 4 - 1 = 3

### Process P3

- CT = 9
- TAT = 9 - 2 = 7
- WT = 7 - 2 = 5
- RT = 7 - 2 = 5

Final results:

| Process | CT | TAT | WT | RT |
|---|---:|---:|---:|---:|
| P1 | 4 | 4 | 0 | 0 |
| P2 | 7 | 6 | 3 | 3 |
| P3 | 9 | 7 | 5 | 5 |

Average waiting time:

`(0 + 3 + 5) / 3 = 2.67`

Average turnaround time:

`(4 + 6 + 7) / 3 = 5.67`

Average response time:

`(0 + 3 + 5) / 3 = 2.67`

---

## 8. Preemptive vs Non-Preemptive Scheduling

| Feature | Preemptive | Non-Preemptive |
|---|---|---|
| CPU interruption | A running process can be interrupted | A running process normally continues until completion |
| Scheduling decisions | Can happen while a process is running | Usually happen when a process finishes or blocks |
| Responsiveness | Often better for interactive tasks | May be less responsive |
| Complexity | Usually more complex | Usually simpler |
| Examples in this project | SRTF, Preemptive Priority, RR, MLQ and MLFQ according to their implementation | FCFS, SJF, Non-Preemptive Priority |

---

## 9. Installation and Execution

### Requirements

- Python 3.9 or a compatible version for the installed dependencies.
- pip package manager.
- The project source code.

### Step 1: Open the Project Folder

Open a terminal or Command Prompt inside the project directory.

Example:

```bash
cd operating-system-simulator
```

Use the actual location of your project folder if it is different.

### Step 2: Create a Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies

If a `requirements.txt` file is included:

```bash
pip install -r requirements.txt
```

Otherwise, install Streamlit and any other packages required by your source code. For example:

```bash
pip install streamlit pandas
```

Install any additional visualization libraries only if your code uses them.

### Step 4: Run the Application

```bash
streamlit run app.py
```

Streamlit will provide a local URL, commonly:

`http://localhost:8501`

Open that URL in your browser if it does not open automatically.

---

## 10. Project Structure

The project is organized into a main application and separate scheduling algorithm modules.

A simplified structure may look like this:

```text
operating-system-simulator/
│
├── app.py
├── README.md
│
└── cpu_scheduling/
    ├── utils.py
    │
    ├── preemptive/
    │   ├── srtf.py
    │   ├── priority.py
    │   ├── round_robin.py
    │   ├── multilevel_queue.py
    │   └── multilevel_feedback.py
    │
    └── non_preemptive/
        ├── fcfs.py
        ├── sjf.py
        └── priority.py
```

**Important:** This is an illustrative structure. File names and locations should match the actual files in your project. If an algorithm is stored in a different module or the folder structure differs, update this section accordingly.

### Main Application: `app.py`

The main application is responsible for:

- Displaying the user interface.
- Allowing users to select an algorithm.
- Collecting process inputs.
- Calling the selected scheduling function.
- Displaying calculated results and visualizations supported by the application.

### Algorithm Modules

Each algorithm module contains the logic for its respective scheduling method. Separating algorithms into individual modules makes the code easier to maintain, test, and extend.

### Utility Module: `utils.py`

Shared functions can be used to calculate result rows, track execution intervals, or support scheduling visualizations, depending on the implementation.

---

## 11. Input Parameters

The required input depends on the selected algorithm.

| Parameter | Description | Used By |
|---|---|---|
| Process ID | Identifies each process | All algorithms |
| Arrival Time | Time the process enters the ready queue | All algorithms |
| Burst Time | CPU time required by the process | All algorithms |
| Priority | Scheduling priority | Priority Scheduling |
| Queue Number | Identifies a process's queue | MLQ |
| Time Quantum | Maximum CPU time per turn | Round Robin |
| Queue Quantums | Time limits associated with feedback queues | MLFQ |

Processes should have valid arrival times and positive burst times. Priority and queue values must follow the conventions used by the application.

---

## 12. Advantages and Limitations

### Advantages

- Provides a practical way to learn CPU scheduling.
- Demonstrates several common scheduling algorithms.
- Helps compare waiting time, turnaround time, and response time.
- Makes scheduling decisions easier to understand through examples and execution timelines.
- Uses Python and Streamlit, which are accessible technologies for student projects.
- Organizes scheduling logic into separate modules.

### Limitations

- The simulator models CPU scheduling rather than every feature of a real operating system.
- Scheduling results depend on the input processes and algorithm settings.
- Context-switch overhead may not be included.
- Some real-world scheduling policies include aging, dynamic priorities, or other mechanisms that are not implemented in this project.
- Predicted-burst SJF requires additional prediction logic if it is to be simulated separately.
- The algorithms should be tested with different arrival times and edge cases to verify their behavior.

---

## 13. Future Improvements

Possible future enhancements include:

- Add a graphical Gantt chart for every scheduling algorithm.
- Compare multiple algorithms using the same input processes.
- Display average waiting, turnaround, and response times together.
- Add CPU utilization and throughput calculations.
- Allow users to save or download scheduling results.
- Add process arrival animations.
- Implement aging to reduce starvation in priority-based algorithms.
- Add SJF using exponential averaging to predict future CPU bursts.
- Improve input validation and error messages.
- Add unit tests for each scheduling algorithm.

---

## 14. Conclusion

The Operating System CPU Scheduling Simulator demonstrates how an operating system chooses processes for CPU execution. It covers FCFS, SJF, SRTF, Priority Scheduling, Round Robin, Multilevel Queue, and Multilevel Feedback Queue scheduling.

By entering process information and examining the execution order and scheduling calculations, students can better understand the differences between algorithms and how these differences affect waiting time, turnaround time, and response time.

The project provides a useful educational foundation for learning CPU scheduling and exploring how operating systems manage competing processes.

---

**Project:** Operating System CPU Scheduling Simulator  
**Language:** Python  
**Framework:** Streamlit  
**Purpose:** Educational demonstration of CPU scheduling algorithms
