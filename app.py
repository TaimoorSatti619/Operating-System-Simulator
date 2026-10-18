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
          <div class="eyebrow">PROCESS MANAGEMENT 2.0</div>
          <h1>Processes &amp; States</h1>
          <p>Manage multiple processes with manual stepping and automatic execution.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "os_processes" not in st.session_state:
        st.session_state.os_processes = []
    if "next_pid" not in st.session_state:
        st.session_state.next_pid = 1
    if "process_auto_run" not in st.session_state:
        st.session_state.process_auto_run = False
    if "process_clock" not in st.session_state:
        st.session_state.process_clock = 0

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
          <span class="state-note">Running → Waiting: I/O request</span>
          <span class="state-note">Waiting → Ready: I/O completed</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    def advance_process():
        """Advance the educational FCFS-style process lifecycle by one tick."""
        items = st.session_state.os_processes

        if not items:
            return

        # Admit the first New process into the Ready state.
        new_process = next(
            (p for p in items if p["state"] == "New"), None
        )
        if new_process:
            transition_process(new_process, "admit")
            st.session_state.process_clock += 1
            return

        # Continue executing the process currently using the CPU.
        running = next(
            (p for p in items if p["state"] == "Running"), None
        )
        if running:
            transition_process(running, "execute_unit")
            st.session_state.process_clock += 1
            return

        # If the CPU is free, dispatch the first Ready process.
        ready = next(
            (p for p in items if p["state"] == "Ready"), None
        )
        if ready:
            transition_process(ready, "dispatch")
            st.session_state.process_clock += 1
            return

        # No Ready, Running or New processes remain.
        st.session_state.process_auto_run = False

    with st.form("create_process_form", clear_on_submit=True):
        st.markdown("### Create a process")
        col1, col2 = st.columns(2)

        process_name = col1.text_input(
            "Process name", placeholder="e.g. Browser"
        )
        process_burst = col2.number_input(
            "CPU burst time",
            min_value=1,
            max_value=999,
            value=5,
            step=1,
        )

        create_clicked = st.form_submit_button(
            "＋ Create Process",
            type="primary",
            use_container_width=True,
        )

    if create_clicked:
        pid = f"P{st.session_state.next_pid}"

        st.session_state.os_processes.append(
            create_process(
                pid,
                process_name.strip() or pid,
                int(process_burst),
            )
        )

        st.session_state.next_pid += 1
        st.session_state.process_auto_run = False
        st.success(f"{pid} created successfully in New state.")
        st.rerun()

    # This fragment refreshes itself during Auto Run.
    @st.fragment(run_every=1.0)
    def process_dashboard():
        items = st.session_state.os_processes

        st.markdown("### Simulation controls")

        a, b, c = st.columns(3)

        with a:
            if st.button(
                "⏭️ Next Step",
                use_container_width=True,
                disabled=not items,
            ):
                st.session_state.process_auto_run = False
                advance_process()
                st.rerun(scope="app")

        with b:
            if st.button(
                "▶️ Auto Run",
                type="primary",
                use_container_width=True,
                disabled=(
                    not items
                    or st.session_state.process_auto_run
                    or all(
                        p["state"] in ("Terminated", "Waiting")
                        for p in items
                    )
                ),
            ):
                st.session_state.process_auto_run = True
                st.rerun(scope="app")

        with c:
            if st.button(
                "⏸️ Pause",
                use_container_width=True,
                disabled=not st.session_state.process_auto_run,
            ):
                st.session_state.process_auto_run = False
                st.rerun(scope="app")

        running_now = next(
            (p for p in items if p["state"] == "Running"), None
        )

        # Automatic simulation: one tick per fragment refresh.
        if st.session_state.process_auto_run:
            advance_process()

            items = st.session_state.os_processes

            unfinished = any(
                p["state"] in ("New", "Ready", "Running")
                for p in items
            )

            if not unfinished:
                st.session_state.process_auto_run = False

        st.markdown(
            f"**Simulation clock:** {st.session_state.process_clock} units"
        )

        if st.session_state.process_auto_run:
            st.info("Auto Run is active. Use Pause to stop the simulation.")
        elif items:
            st.caption("Paused. Use Next Step or Auto Run to continue.")

        if not items:
            st.info("Create your first process above to start.")
            return

        # Current process and process table.
        running = next(
            (p for p in items if p["state"] == "Running"), None
        )

        if running:
            st.success(
                f"CPU is executing: {running['pid']} · {running['name']}"
            )
        else:
            st.info("CPU is idle. A Ready process can be dispatched.")

        rows = [
            {
                "PID": p["pid"],
                "Name": p["name"],
                "State": p["state"],
                "CPU Burst": p["burst_time"],
                "Remaining": p["remaining_time"],
                "Last Transition": p["last_transition"],
            }
            for p in items
        ]

        st.markdown("### Live process table")
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Individual process controls")
        selected_pid = st.selectbox(
            "Select process",
            options=[p["pid"] for p in items],
            format_func=lambda pid: next(
                f'{p["pid"]} · {p["name"]} ({p["state"]})'
                for p in items if p["pid"] == pid
            ),
            key="process_selected_pid",
        )

        selected = next(
            p for p in items if p["pid"] == selected_pid
        )

        st.markdown(
            f"""
            <div class="current-state">
              <span>Selected process</span>
              <strong>{selected["pid"]} · {selected["name"]}</strong>
              <span class="state-pill">{selected["state"]}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        actions = get_available_actions(selected["state"])

        labels = {
            "admit": "Admit to Ready",
            "dispatch": "Dispatch to Running",
            "execute_unit": "Execute 1 CPU Unit",
            "request_io": "Request I/O",
            "complete_io": "Complete I/O",
            "preempt": "Preempt to Ready",
            "terminate": "Terminate Process",
        }

        if actions:
            action_cols = st.columns(min(3, len(actions)))

            for i, action in enumerate(actions):
                with action_cols[i % len(action_cols)]:
                    if st.button(
                        labels[action],
                        key=f"manual_{selected_pid}_{action}",
                        use_container_width=True,
                    ):
                        st.session_state.process_auto_run = False
                        transition_process(selected, action)
                        st.rerun(scope="app")
        else:
            st.info("This process has terminated.")

        left, right = st.columns([1.5, 1])

        with left:
            st.markdown("### Process state summary")

            for state in (
                "New", "Ready", "Running", "Waiting", "Terminated"
            ):
                count = sum(
                    p["state"] == state for p in items
                )
                st.write(f"**{state}:** {count}")

        with right:
            st.markdown("### Process Control Block")

            st.markdown(
                f"""
                <div class="pcb-card">
                  <div class="pcb-row"><span>PID</span><b>{selected["pid"]}</b></div>
                  <div class="pcb-row"><span>Name</span><b>{selected["name"]}</b></div>
                  <div class="pcb-row"><span>State</span><b>{selected["state"]}</b></div>
                  <div class="pcb-row"><span>CPU Burst</span><b>{selected["burst_time"]}</b></div>
                  <div class="pcb-row"><span>Remaining</span><b>{selected["remaining_time"]}</b></div>
                  <div class="pcb-row"><span>Last Transition</span><b>{selected["last_transition"]}</b></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        if st.button("🗑️ Reset All Processes", type="secondary"):
            st.session_state.process_auto_run = False
            st.session_state.os_processes = []
            st.session_state.next_pid = 1
            st.session_state.process_clock = 0
            st.rerun(scope="app")

    process_dashboard()


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
