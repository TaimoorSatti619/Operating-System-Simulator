"""State transitions for the educational process lifecycle simulator."""

STATES = ("New", "Ready", "Running", "Waiting", "Terminated")

TRANSITIONS = {
    "New": {"admit": "Ready"},
    "Ready": {"dispatch": "Running"},
    "Running": {
        "execute_unit": "Running",
        "request_io": "Waiting",
        "preempt": "Ready",
        "terminate": "Terminated",
    },
    "Waiting": {"complete_io": "Ready"},
    "Terminated": {},
}


def create_process(pid: str, name: str, burst_time: int) -> dict:
    """Create a process in the New state."""
    if not pid or not name:
        raise ValueError("PID and process name are required.")
    if int(burst_time) <= 0:
        raise ValueError("Burst time must be greater than zero.")
    return {
        "pid": str(pid),
        "name": str(name),
        "state": "New",
        "burst_time": int(burst_time),
        "remaining_time": int(burst_time),
        "last_transition": "Created",
    }


def get_available_actions(state: str) -> list[str]:
    """Return actions allowed from the current state."""
    return list(TRANSITIONS.get(state, {}).keys())


def transition_process(process: dict, action: str) -> dict:
    """Apply one valid state transition and update simple burst-time tracking."""
    state = process["state"]
    if action not in TRANSITIONS.get(state, {}):
        raise ValueError(f"Action '{action}' is not valid from state '{state}'.")

    if action == "execute_unit":
        process["remaining_time"] = max(0, int(process["remaining_time"]) - 1)
        if process["remaining_time"] == 0:
            process["state"] = "Terminated"
            process["last_transition"] = "Running → Terminated (burst completed)"
            return process
        process["state"] = "Running"
        process["last_transition"] = f"Executed 1 CPU unit; {process['remaining_time']} remaining"
        return process

    new_state = TRANSITIONS[state][action]
    process["state"] = new_state
    process["last_transition"] = f"{state} → {new_state}"
    return process
