
from collections import deque
from cpu_scheduling.utils import build_rows, append_gantt


def multilevel_feedback_queue(
    processes, quantums=(2, 4, 8)
):
    """
    Simplified Multilevel Feedback Queue.
    All processes start in Q1.
    Q1 quantum = 2
    Q2 quantum = 4
    Q3 quantum = 8
    Unfinished processes move to a lower-priority queue.
    """

    if any(q <= 0 for q in quantums):
        raise ValueError("Quantums must be positive.")

    ps = sorted(
        processes,
        key=lambda p: (p["at"], p["pid"])
    )

    remaining = {
        p["pid"]: p["bt"] for p in ps
    }

    completion = {}
    first_start = {}
    gantt = []

    queues = [deque() for _ in quantums]
    added = set()
    t = min(p["at"] for p in ps)

    def add_arrivals():
        for p in ps:
            pid = p["pid"]

            if (
                p["at"] <= t
                and pid not in added
                and remaining[pid] > 0
            ):
                queues[0].append(p)
                added.add(pid)

    add_arrivals()

    while remaining:
        add_arrivals()

        qidx = next(
            (
                i for i, queue in enumerate(queues)
                if queue
            ),
            None
        )

        if qidx is None:
            t += 1
            add_arrivals()
            continue

        p = queues[qidx].popleft()
        pid = p["pid"]

        first_start.setdefault(pid, t)

        quantum = quantums[qidx]
        used = 0

        while (
            used < quantum
            and remaining.get(pid, 0) > 0
        ):
            # New Q1 arrivals interrupt lower queues
            if qidx > 0:
                add_arrivals()

                if queues[0]:
                    break

            append_gantt(gantt, pid, t, t + 1)

            remaining[pid] -= 1
            t += 1
            used += 1

            add_arrivals()

        if remaining.get(pid, 0) == 0:
            completion[pid] = t
            del remaining[pid]
        else:
            # Demote if its complete quantum was used
            if (
                used >= quantum
                and qidx < len(queues) - 1
            ):
                next_queue = qidx + 1
            else:
                next_queue = qidx

            queues[next_queue].append(p)

    result = build_rows(
        processes, completion, first_start
    )

    result["gantt"] = gantt
    return result
