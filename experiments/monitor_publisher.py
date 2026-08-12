###################################################################################
# monitor_publisher.py, EDGE TO CLOUD FAULT DIAGNOSIS - RESOURCE MONITOR
# Cross-platform (Linux/Windows) CPU/RAM logger for every Publisher.py process
# running on this host, used to record per-device hardware usage during
# scalability runs (including several simulated devices sharing one host).
# Not a runtime dependency of the framework itself (pip install psutil first).
###################################################################################

import csv
import time

import psutil


def _device_name(cmdline):
    for i, part in enumerate(cmdline):
        if part == "--device" and i + 1 < len(cmdline):
            return cmdline[i + 1]
    return "unknown"


def find_publisher_procs():
    groups = {}
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
        if not any("Publisher.py" in part for part in cmdline):
            continue
        device = _device_name(cmdline)
        groups.setdefault(device, []).append(psutil.Process(p.info["pid"]))

    result = {}
    for device, procs in groups.items():
        if len(procs) == 1:
            result[device] = procs[0]
        else:
            # More than one process for the same --device also happens on Windows,
            # where a venv's python.exe can be a launcher that re-execs the real
            # interpreter as a child - both match on cmdline text but only the
            # child actually imports pandas/numpy and does work. The idle launcher
            # sits near-zero RSS, so the busy one is the max by memory.
            result[device] = max(procs, key=lambda proc: proc.memory_info().rss)
    return result


def main():
    interval = 5.0
    tracked = {}

    with open("resource_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "device", "cpu_percent", "rss_mb"])
        print(f"Monitoring Publisher.py processes every {interval}s -> resource_log.csv (Ctrl+C to stop)")

        while True:
            current = find_publisher_procs()

            for device, proc in current.items():
                if device not in tracked or tracked[device].pid != proc.pid:
                    tracked[device] = proc
                    tracked[device].cpu_percent(interval=None)  # prime, first read is always 0

            for device in list(tracked):
                if device not in current:
                    del tracked[device]

            time.sleep(interval)
            ts = time.strftime("%Y-%m-%d %H:%M:%S")

            for device, proc in list(tracked.items()):
                try:
                    cpu = proc.cpu_percent(interval=None)
                    rss_mb = round(proc.memory_info().rss / (1024 * 1024), 1)
                except psutil.NoSuchProcess:
                    del tracked[device]
                    continue
                writer.writerow([ts, device, cpu, rss_mb])
                print(f"{device}: cpu={cpu:5.1f}%  rss={rss_mb:7.1f} MB")
            f.flush()

            if not tracked:
                print("No Publisher.py processes running - waiting...")


if __name__ == "__main__":
    main()
