from cpu_scheduling.utils import build_rows, append_gantt

def fcfs(processes):
    ps = sorted(processes, key=lambda p: (p["at"], p["pid"]))
    t, completion, first_start, gantt = 0, {}, {}, []
    for p in ps:
        if t < p["at"]:
            t = p["at"]
        start = t
        first_start.setdefault(p["pid"], start)
        t += p["bt"]
        completion[p["pid"]] = t
        append_gantt(gantt, p["pid"], start, t)
    out = build_rows(processes, completion, first_start)
    out["gantt"] = gantt
    return out
