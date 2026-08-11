###################################################################################
# monitor_publisher.py, EDGE TO CLOUD FAULT DIAGNOSIS - RESOURCE MONITOR
# Cross-platform (Linux/Windows) CPU/RAM logger for a running Publisher.py
# process, used to record per-device hardware usage during scalability runs.
# Not a runtime dependency of the framework itself (pip install psutil first).
###################################################################################

import csv
import sys
import time

import psutil


def find_publisher_proc():
    candidates = []
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        cmdline = p.info.get("cmdline") or []
        if not cmdline:
            continue
        # Require the executable itself to be python, not just any process whose
        # command line happens to mention "Publisher.py" - e.g. a `bash -c "...
        # python Publisher.py ... | tee log"` wrapper shell also matches on text
        # alone, and is a different (idle) process from the real one doing work.
        exe = cmdline[0].lower()
        name = (p.info.get("name") or "").lower()
        if "python" not in exe and "python" not in name:
            continue
        if any("Publisher.py" in part for part in cmdline):
            candidates.append(psutil.Process(p.info["pid"]))
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    # More than one match also happens on Windows, where a venv's python.exe can be
    # a launcher that re-execs the real interpreter as a child - both match on
    # cmdline text but only the child actually imports pandas/numpy and does work.
    # The idle launcher sits near-zero RSS, so the busy one is the max by memory.
    return max(candidates, key=lambda proc: proc.memory_info().rss)


def main():
    proc = find_publisher_proc()
    if proc is None:
        sys.exit("Publisher.py process not found - start it first")

    proc.cpu_percent(interval=None)  # prime the internal counter, first read is always 0
    interval = 5.0

    with open("resource_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "cpu_percent", "rss_mb"])
        print(f"Monitoring PID {proc.pid} every {interval}s -> resource_log.csv (Ctrl+C to stop)")
        while True:
            time.sleep(interval)
            cpu = proc.cpu_percent(interval=None)
            rss_mb = round(proc.memory_info().rss / (1024 * 1024), 1)
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), cpu, rss_mb])
            f.flush()
            print(f"cpu={cpu:5.1f}%  rss={rss_mb:7.1f} MB")


if __name__ == "__main__":
    main()
