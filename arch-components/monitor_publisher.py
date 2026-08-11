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
    for p in psutil.process_iter(["pid", "cmdline"]):
        cmdline = p.info.get("cmdline") or []
        if any("Publisher.py" in part for part in cmdline):
            return psutil.Process(p.info["pid"])
    return None


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
