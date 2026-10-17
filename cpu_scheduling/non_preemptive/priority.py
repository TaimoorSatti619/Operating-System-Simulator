from cpu_scheduling.utils import build_rows, append_gantt

def non_preemptive_priority(processes):
    remaining = {p["pid"]: p.copy() for p in processes}
    t, completion, first_start, gantt = 0, {}, {}, []
    while remaining:
        ready = [p for p in remaining.values() if p["at"] <= t]
        if not ready:
            t = min(p["at"] for p in remaining.values())
            continue
        p = min(ready, key=lambda x: (x.get("priority", 999), x["at"], x["pid"]))
        start = t
        first_start[p["pid"]] = start
        t += p["bt"]
        completion[p["pid"]] = t
        append_gantt(gantt, p["pid"], start, t)
        del remaining[p["pid"]]
    out = build_rows(processes, completion, first_start)
    out["gantt"] = gantt
    return out
