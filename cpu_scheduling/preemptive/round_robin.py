from collections import deque
from cpu_scheduling.utils import build_rows, append_gantt

def round_robin(processes, quantum):
    if quantum <= 0:
        raise ValueError("Time quantum must be greater than zero.")
    ps = sorted(processes, key=lambda p: (p["at"], p["pid"]))
    remaining = {p["pid"]: p["bt"] for p in ps}
    completion, first_start, gantt = {}, {}, []
    ready, i = deque(), 0
    t = ps[0]["at"]
    while i < len(ps) and ps[i]["at"] <= t:
        ready.append(ps[i]); i += 1
    while ready or i < len(ps):
        if not ready:
            t = max(t, ps[i]["at"])
            while i < len(ps) and ps[i]["at"] <= t:
                ready.append(ps[i]); i += 1
        p = ready.popleft()
        pid = p["pid"]
        first_start.setdefault(pid, t)
        run = min(quantum, remaining[pid])
        end = t + run
        append_gantt(gantt, pid, t, end)
        t = end
        remaining[pid] -= run
        while i < len(ps) and ps[i]["at"] <= t:
            ready.append(ps[i]); i += 1
        if remaining[pid] > 0:
            ready.append(p)
        else:
            completion[pid] = t
    out = build_rows(processes, completion, first_start)
    out["gantt"] = gantt
    return out
