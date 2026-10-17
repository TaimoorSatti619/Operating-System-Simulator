from cpu_scheduling.utils import build_rows, append_gantt

def srtf(processes):
    remaining = {p["pid"]: p["bt"] for p in processes}
    completion, first_start, gantt = {}, {}, []
    t = min(p["at"] for p in processes)
    while remaining:
        ready = [p for p in processes if p["at"] <= t and remaining.get(p["pid"], 0) > 0]
        if not ready:
            t += 1
            continue
        p = min(ready, key=lambda x: (remaining[x["pid"]], x["at"], x["pid"]))
        first_start.setdefault(p["pid"], t)
        append_gantt(gantt, p["pid"], t, t+1)
        remaining[p["pid"]] -= 1
        t += 1
        if remaining[p["pid"]] == 0:
            completion[p["pid"]] = t
            del remaining[p["pid"]]
    out = build_rows(processes, completion, first_start)
    out["gantt"] = gantt
    return out
