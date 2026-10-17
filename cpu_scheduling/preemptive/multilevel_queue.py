
from cpu_scheduling.utils import build_rows, append_gantt


def multilevel_queue(processes):
    """
    Fixed Multilevel Queue Scheduling.
    Queue 1 has the highest priority.
    Queue 2 has medium priority.
    Queue 3 has the lowest priority.
    Processes stay in their assigned queues.
    """

    remaining = {
        p["pid"]: p["bt"] for p in processes
    }

    completion = {}
    first_start = {}
    gantt = []

    t = min(p["at"] for p in processes)

    while remaining:
        ready = [
            p for p in processes
            if p["at"] <= t
            and remaining.get(p["pid"], 0) > 0
        ]

        if not ready:
            t += 1
            continue

        # Smaller queue number = higher priority
        p = min(
            ready,
            key=lambda x: (
                x.get("queue", 3),
                x["at"],
                x["pid"]
            )
        )

        pid = p["pid"]

        first_start.setdefault(pid, t)

        # Execute for one time unit
        append_gantt(gantt, pid, t, t + 1)

        remaining[pid] -= 1
        t += 1

        if remaining[pid] == 0:
            completion[pid] = t
            del remaining[pid]

    result = build_rows(
        processes, completion, first_start
    )

    result["gantt"] = gantt
    return result
