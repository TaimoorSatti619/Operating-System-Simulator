import time
import streamlit as st
import pandas as pd

from cpu_scheduling.preemptive.srtf import srtf
from cpu_scheduling.preemptive.priority import preemptive_priority
from cpu_scheduling.preemptive.round_robin import round_robin
from cpu_scheduling.non_preemptive.fcfs import fcfs
from cpu_scheduling.non_preemptive.sjf import sjf
from cpu_scheduling.non_preemptive.priority import non_preemptive_priority
from cpu_scheduling.preemptive.multilevel_queue import multilevel_queue
from cpu_scheduling.preemptive.multilevel_feedback import multilevel_feedback_queue

from processes.state_machine import (
    create_process,
    get_available_actions,
    transition_process,
    STATES,
)

st.set_page_config(
    page_title="Operating System Simulator",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css():
    try:
        with open("assets/style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

def show_startup_splash():
    """Show once per browser session, not on every Streamlit rerun."""
    if st.session_state.get("startup_seen", False):
        return

    splash = st.empty()
    splash.markdown(
        """
        <div class="splash-wrap">
          <div class="splash-orbit orbit-one"></div>
          <div class="splash-orbit orbit-two"></div>
          <div class="splash-orbit orbit-three"></div>
          <div class="cpu-logo">
            <div class="cpu-pins"></div>
            <div class="cpu-chip">
              <div class="cpu-core"></div>
              <span>OS</span>
            </div>
          </div>
          <div class="splash-title">OS <span>SIMULATOR</span></div>
          <div class="splash-subtitle">INITIALIZING SYSTEM MODULES</div>
          <div class="loading-track"><div class="loading-fill"></div></div>
          <div class="loading-caption">Preparing your interactive learning environment...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    progress = st.progress(0, text="Booting simulator...")
    for value, message in [
        (22, "Loading core interface..."),
        (48, "Initializing process manager..."),
        (73, "Preparing scheduling modules..."),
        (100, "System ready."),
    ]:
        progress.progress(value, text=message)
        time.sleep(0.22)
    time.sleep(0.25)
    progress.empty()
    splash.empty()
    st.session_state.startup_seen = True

show_startup_splash()

st.sidebar.markdown(
    """
    <div class="sidebar-brand">
      <div class="sidebar-logo">▦</div>
      <div><div class="sidebar-title">OS SIMULATOR</div>
      <div class="sidebar-subtitle">INTERACTIVE LAB</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)
section = st.sidebar.radio(
    "NAVIGATION",
    ["Home", "Processes", "CPU Scheduling", "Process Synchronization"],
    key="main_navigation",
)
st.sidebar.divider()
# st.sidebar.caption("More operating-system modules can be added here.")

if section == "Home":
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">INTERACTIVE LEARNING PLATFORM</div>
          <h1>OPERATING SYSTEM</h1>
          <p>Explore process management and CPU scheduling through interactive simulations.</p>
          <div class="hero-glow"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)
    a.metric("Available Modules", "2")
    b.metric("CPU Algorithms", "7")
    c.metric("Next Module", "Synchronization")
    st.info("Choose **Processes** to explore process states, or **CPU Scheduling** to run an algorithm.")

elif section == "Processes":
    st.markdown(
        """
        <div class="page-head">
          <div class="eyebrow">PROCESS MANAGEMENT</div>
          <h1>Processes &amp; States</h1>
          <p>Create a process and explore how it moves through the operating system lifecycle.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "os_processes" not in st.session_state:
        st.session_state.os_processes = []
    if "next_pid" not in st.session_state:
        st.session_state.next_pid = 1

    processes = st.session_state.os_processes

    st.markdown("### Process lifecycle")
    st.markdown(
        """
        <div class="state-flow">
          <div class="state-node state-new"><b>NEW</b><small>Created</small></div>
          <div class="state-arrow">→</div>
          <div class="state-node state-ready"><b>READY</b><small>Waiting for CPU</small></div>
          <div class="state-arrow">→</div>
          <div class="state-node state-running"><b>RUNNING</b><small>Using CPU</small></div>
          <div class="state-arrow">→</div>
          <div class="state-node state-terminated"><b>TERMINATED</b><small>Finished</small></div>
        </div>
        <div class="state-flow state-flow-secondary">
          <span class="state-note">Running → Waiting: requests I/O</span>
          <span class="state-note">Waiting → Ready: I/O completes</span>
          <span class="state-note">Running → Ready: preemption</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("This is a simplified five-state process model. Transitions are controlled manually for learning.")

    with st.form("create_process_form", clear_on_submit=True):
        st.markdown("### Create a process")
        pcol1, pcol2 = st.columns(2)
        process_name = pcol1.text_input("Process name", placeholder="e.g. Browser")
        process_burst = pcol2.number_input("CPU burst time (units)", min_value=1, max_value=999, value=5)
        create_clicked = st.form_submit_button("＋ Create Process", type="primary", use_container_width=True)

    if create_clicked:
        pid = f"P{st.session_state.next_pid}"
        new_process = create_process(pid, process_name.strip() or pid, int(process_burst))
        st.session_state.os_processes.append(new_process)
        st.session_state.next_pid += 1
        st.success(f"{pid} created in the New state.")
        st.rerun()

    if processes:
        st.markdown("### Transition controls")
        selected_pid = st.selectbox(
            "Select process",
            options=[p["pid"] for p in processes],
            format_func=lambda pid: next(
                f'{p["pid"]} · {p["name"]} ({p["state"]})'
                for p in processes if p["pid"] == pid
            ),
        )
        selected = next(p for p in processes if p["pid"] == selected_pid)
        st.markdown(
            f'<div class="current-state"><span>Selected process</span><strong>{selected["pid"]} · {selected["name"]}</strong>'
            f'<span class="state-pill">{selected["state"]}</span></div>',
            unsafe_allow_html=True,
        )

        actions = get_available_actions(selected["state"])
        if actions:
            labels = {
                "admit": "Admit to Ready",
                "dispatch": "Dispatch to Running",
                "execute_unit": "Execute 1 CPU Unit",
                "request_io": "Request I/O (Waiting)",
                "complete_io": "Complete I/O (Ready)",
                "preempt": "Preempt to Ready",
                "terminate": "Terminate Process",
            }
            action_cols = st.columns(min(3, len(actions)))
            for i, action in enumerate(actions):
                with action_cols[i % len(action_cols)]:
                    if st.button(labels[action], key=f"{selected_pid}_{action}", use_container_width=True):
                        transition_process(selected, action)
                        st.rerun()
        else:
            st.info("This process has terminated. Create another process to continue.")

        left, right = st.columns([1.5, 1])
        with left:
            st.markdown("### Process table")
            table_rows = [
                {
                    "PID": p["pid"],
                    "Name": p["name"],
                    "State": p["state"],
                    "CPU Burst": p["burst_time"],
                    "Remaining": p["remaining_time"],
                }
                for p in processes
            ]
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
        with right:
            st.markdown("### Process Control Block (PCB)")
            st.markdown(
                f"""
                <div class="pcb-card">
                  <div class="pcb-row"><span>Process ID</span><b>{selected["pid"]}</b></div>
                  <div class="pcb-row"><span>Process name</span><b>{selected["name"]}</b></div>
                  <div class="pcb-row"><span>Current state</span><b>{selected["state"]}</b></div>
                  <div class="pcb-row"><span>CPU burst</span><b>{selected["burst_time"]}</b></div>
                  <div class="pcb-row"><span>Remaining time</span><b>{selected["remaining_time"]}</b></div>
                  <div class="pcb-row"><span>Last transition</span><b>{selected["last_transition"]}</b></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("Reset all processes", type="secondary"):
            st.session_state.os_processes = []
            st.session_state.next_pid = 1
            st.rerun()
    else:
        st.info("No processes yet. Create your first process above to start the simulation.")

elif section == "Process Synchronization":
    st.markdown(
        """
        <div class="page-head">
          <div class="eyebrow">CONCURRENCY</div>
          <h1>Process Synchronization</h1>
          <p>This module is reserved for a future development phase.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("This module is reserved for the next development phase.")

else:
    st.markdown(
        """
        <div class="page-head">
          <div class="eyebrow">CPU MANAGEMENT</div>
          <h1>CPU Scheduling</h1>
          <p>Choose a scheduling type, enter process details, and calculate the results.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    mode = st.radio("Scheduling type", ["Preemptive", "Non-Preemptive"], horizontal=True)
    options = {
        "Preemptive": [
            "SRTF (Preemptive SJF)", "Priority Scheduling", "Round Robin (RR)",
            "Multilevel Queue (MLQ)", "Multilevel Feedback Queue (MLFQ)"
        ],
        "Non-Preemptive": ["FCFS", "SJF", "Priority Scheduling"],
    }
    algorithm = st.selectbox("Choose algorithm", options[mode])
    st.caption({
        "SRTF (Preemptive SJF)": "The process with the shortest remaining CPU time runs first.",
        "Priority Scheduling": "The process with the highest priority runs first. Smaller priority number means higher priority.",
        "Round Robin (RR)": "Each ready process receives a fixed time quantum in turn.",
        "FCFS": "Processes run in order of arrival.",
        "SJF": "The available process with the shortest burst time runs first.",
        "Multilevel Queue (MLQ)": "Processes are assigned to fixed queues, each with its own priority.",
        "Multilevel Feedback Queue (MLFQ)": "Processes can move between queues based on their execution and time quantum."
    }[algorithm])

    n = st.number_input("Number of processes", min_value=1, max_value=12, value=4, step=1)
    default = pd.DataFrame({
        "Process": [f"P{i+1}" for i in range(int(n))],
        "Arrival Time": [0] + [i for i in range(1, int(n))],
        "Burst Time": [5, 3, 8, 2][:int(n)] if int(n) <= 4 else [5] + [3 for _ in range(int(n)-1)],
        "Priority": [2, 1, 3, 2][:int(n)] if int(n) <= 4 else [2 for _ in range(int(n))],
        "Queue": [1, 2, 1, 3][:int(n)] if int(n) <= 4 else [1 + (i % 3) for i in range(int(n))],
    })
    with st.form("process_form"):
        st.write("### Process input")
        edited = st.data_editor(default, num_rows="fixed", use_container_width=True, key=f"editor_{n}_{mode}_{algorithm}")
        quantum = None
        if algorithm == "Round Robin (RR)":
            quantum = st.number_input("Time Quantum", min_value=1, value=2, step=1)
        submitted = st.form_submit_button("▶ Calculate Schedule", type="primary", use_container_width=True)

    if submitted:
        try:
            if edited[["Arrival Time", "Burst Time"]].isnull().any().any():
                raise ValueError("Arrival Time and Burst Time cannot be empty.")
            if (edited["Arrival Time"] < 0).any():
                raise ValueError("Arrival Time cannot be negative.")
            if (edited["Burst Time"] <= 0).any():
                raise ValueError("Burst Time must be greater than zero.")
            if "Priority" in edited and edited["Priority"].isnull().any():
                raise ValueError("Priority cannot be empty.")
            if "Queue" in edited and edited["Queue"].isnull().any():
                raise ValueError("Queue cannot be empty.")

            processes = []
            for _, row in edited.iterrows():
                p = {"pid": str(row["Process"]), "at": int(row["Arrival Time"]), "bt": int(row["Burst Time"])}
                if "Priority" in row:
                    p["priority"] = int(row["Priority"])
                if "Queue" in row:
                    q = int(row["Queue"])
                    if q not in (1, 2, 3):
                        raise ValueError("Queue must be 1, 2, or 3.")
                    p["queue"] = q
                processes.append(p)

            if algorithm == "FCFS":
                result = fcfs(processes)
            elif algorithm == "SJF":
                result = sjf(processes)
            elif algorithm == "SRTF (Preemptive SJF)":
                result = srtf(processes)
            elif algorithm == "Priority Scheduling" and mode == "Preemptive":
                result = preemptive_priority(processes)
            elif algorithm == "Priority Scheduling":
                result = non_preemptive_priority(processes)
            elif algorithm == "Multilevel Queue (MLQ)":
                result = multilevel_queue(processes)
            elif algorithm == "Multilevel Feedback Queue (MLFQ)":
                result = multilevel_feedback_queue(processes)
            else:
                result = round_robin(processes, int(quantum))

            st.success("Scheduling completed successfully.")
            st.subheader("Gantt Chart")
            chunks = result["gantt"]
            cols = st.columns(len(chunks)) if chunks else []
            for col, chunk in zip(cols, chunks):
                with col:
                    st.markdown(
                        f"<div class='gantt-block'><b>{chunk['pid']}</b><small>{chunk['start']} – {chunk['end']}</small></div>",
                        unsafe_allow_html=True,
                    )
            st.subheader("Process Results")
            df = pd.DataFrame(result["rows"])
            st.dataframe(df, use_container_width=True, hide_index=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("Average Waiting Time", f"{df['WT'].mean():.2f}")
            m2.metric("Average Turnaround Time", f"{df['TAT'].mean():.2f}")
            m3.metric("Average Response Time", f"{df['RT'].mean():.2f}")
        except Exception as e:
            st.error(f"Please check your inputs: {e}")

    with st.expander("Formula reference"):
        st.markdown("""
        - **Turnaround Time (TAT) = Completion Time (CT) − Arrival Time (AT)**
        - **Waiting Time (WT) = Turnaround Time (TAT) − Burst Time (BT)**
        - **Response Time (RT) = First Start Time − Arrival Time (AT)**
        - **Priority:** smaller priority number means higher priority.
        """)
