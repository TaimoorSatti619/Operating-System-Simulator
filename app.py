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




st.set_page_config(page_title="Operating System Simulator", page_icon="🖥️", layout="wide")

def load_css():
    try:
        with open("assets/style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()
st.sidebar.markdown("# OS Simulator")
st.sidebar.caption("Interactive learning platform")

section = st.sidebar.radio("NAVIGATION", ["Home", "CPU Scheduling", "Process Synchronization"])

st.sidebar.divider()
# st.sidebar.caption("More modules will be added later.")

if section == "Home":
    st.markdown("<div class='hero'><div class='eyebrow'>INTERACTIVE LEARNING PLATFORM</div><h1>OPERATING SYSTEM</h1><p>Understand operating-system concepts by running interactive simulations.</p></div>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric("Available Module", "CPU Scheduling")
    b.metric("Algorithms", "6")
    c.metric("Coming Next", "Synchronization")
    st.info("Choose **CPU Scheduling** from the sidebar to run an algorithm.")
elif section == "Process Synchronization":
    st.title("Process Synchronization")
    st.info("This module is reserved for the next development phase.")
else:
    st.markdown("<div class='page-head'><div class='eyebrow'>CHAPTER 5</div><h1>CPU Scheduling</h1><p>Choose a scheduling type, enter process details, and calculate the results.</p></div>", unsafe_allow_html=True)
    mode = st.radio("Scheduling type", ["Preemptive", "Non-Preemptive"], horizontal=True)
    options = {
        "Preemptive": ["SRTF (Preemptive SJF)", "Priority Scheduling", "Round Robin (RR)","Multilevel Queue (MLQ)", "Multilevel Feedback Queue (MLFQ)"],
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
        "Queue": [1, 2, 1, 3][:int(n)]
          if int(n) <= 4
          else [1 + (i % 3) for i in range(int(n))]
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
                    st.markdown(f"<div class='gantt-block'><b>{chunk['pid']}</b><small>{chunk['start']} – {chunk['end']}</small></div>", unsafe_allow_html=True)
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
