
"""Process lifecycle and state transitions."""

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


def create_process(pid, name, burst_time):
    burst_time = int(burst_time)

    if burst_time <= 0:
        raise ValueError("Burst time must be greater than zero.")

    return {
        "pid": str(pid),
        "name": str(name),
        "state": "New",
        "burst_time": burst_time,
        "remaining_time": burst_time,
        "last_transition": "Created",
    }


def get_available_actions(state):
    return list(TRANSITIONS.get(state, {}).keys())


def transition_process(process, action):
    state = process["state"]
    allowed = TRANSITIONS.get(state, {})

    if action not in allowed:
        raise ValueError(
            f"Action {action} is invalid from {state}."
        )

    if action == "execute_unit":
        process["remaining_time"] = max(
            0, process["remaining_time"] - 1
        )

        if process["remaining_time"] == 0:
            process["state"] = "Terminated"
            process["last_transition"] = (
                "Running → Terminated (burst completed)"
            )
            return process

        process["state"] = "Running"
        process["last_transition"] = (
            f"Executed 1 CPU unit; "
            f"{process['remaining_time']} remaining"
        )
        return process

    new_state = allowed[action]
    process["state"] = new_state
    process["last_transition"] = f"{state} → {new_state}"

    return process
