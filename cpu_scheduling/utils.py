def build_rows(processes, completion, first_start):
    rows = []
    for p in processes:
        pid = p["pid"]
        ct = completion[pid]
        tat = ct - p["at"]
        wt = tat - p["bt"]
        rt = first_start[pid] - p["at"]
        rows.append({"Process": pid, "AT": p["at"], "BT": p["bt"],
                     "CT": ct, "TAT": tat, "WT": wt, "RT": rt})
    return {"rows": rows}

def append_gantt(gantt, pid, start, end):
    if end <= start:
        return
    if gantt and gantt[-1]["pid"] == pid and gantt[-1]["end"] == start:
        gantt[-1]["end"] = end
    else:
        gantt.append({"pid": pid, "start": start, "end": end})
