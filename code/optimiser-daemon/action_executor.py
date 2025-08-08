import psutil
import subprocess
from config import LOW_PRIORITY_SERVICES, PROTECTED_SERVICES

# Track last I/O counters per PID to compute I/O rate
_last_io = {}  # pid → (read_bytes, write_bytes)

def choose_action(state, agent):
    return agent.choose_action(state)

def apply_action(action_type, state):
    action_detail = {"type": action_type}
    total_mem = state["mem_total_mb"]
    mem_threshold = total_mem * 0.05  # 5% of total RAM

    print(f"[Action] Chosen: {action_type}")

    if action_type == "do_nothing":
        print("Doing nothing.")
        action_detail["target"] = None

    elif action_type == "suggest_stop_low_priority_service":
        # Find *all* low-priority services above threshold
        services = analyze_running_services()
        candidates = [
            {"name": s["name"], "mem_mb": s["mem_mb"]}
            for s in services
            if s["priority"] == "low" and s["mem_mb"] and s["mem_mb"] > mem_threshold
        ]
        if candidates:
            # Sort by mem descending
            candidates.sort(key=lambda x: x["mem_mb"], reverse=True)
            msgs = [f"{c['name']} ({c['mem_mb']} MB)" for c in candidates]
            print("Suggest stopping services: " + "; ".join(msgs))
            action_detail["target"] = candidates
        else:
            print("No suitable low-priority services found.")
            action_detail["target"] = None

    elif action_type == "suggest_renice_heavy_process":
        # Find *all* heavy processes above threshold
        candidates = []
        for p in psutil.process_iter(['pid', 'name', 'memory_info']):
            pid = p.info['pid']
            name = p.info['name']

            # Skip kernel and systemd
            if pid == 0 or name == 'systemd':
                continue
            # Skip protected names
            if name in PROTECTED_SERVICES:
                continue

            # Disk I/O delta filter
            try:
                io = p.io_counters()
                prev_read, prev_write = _last_io.get(pid, (io.read_bytes, io.write_bytes))
                delta = (io.read_bytes - prev_read) + (io.write_bytes - prev_write)
                _last_io[pid] = (io.read_bytes, io.write_bytes)
                if delta > 10 * 1024 * 1024:
                    continue
            except Exception:
                continue

            mem_mb = p.info['memory_info'].rss / (1024 * 1024)
            if mem_mb > mem_threshold:
                candidates.append({"pid": pid, "name": name, "mem_mb": round(mem_mb, 2)})

        if candidates:
            candidates.sort(key=lambda x: x["mem_mb"], reverse=True)
            msgs = [f"{c['name']} (PID {c['pid']}) – {c['mem_mb']} MB" for c in candidates]
            print("Suggest renicing processes: " + "; ".join(msgs))
            action_detail["target"] = candidates
        else:
            print("No heavy processes found above threshold.")
            action_detail["target"] = None

    else:
        print("Unknown action.")
        action_detail["target"] = None

    return action_detail


def analyze_running_services():
    service_info_list = []
    try:
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager"],
            stdout=subprocess.PIPE, text=True
        )
        for line in result.stdout.splitlines():
            parts = line.split()
            if not parts or not parts[0].endswith(".service"):
                continue

            service_name = parts[0]
            pid = find_pid_by_service_name(service_name)
            if pid is None:
                continue

            try:
                mem_mb = psutil.Process(pid).memory_info().rss / (1024 * 1024)
            except Exception:
                mem_mb = None

            priority = (
                "protected" if service_name in PROTECTED_SERVICES else
                "low"       if service_name in LOW_PRIORITY_SERVICES else
                "normal"
            )
            service_info_list.append({
                "name": service_name,
                "pid": pid,
                "mem_mb": round(mem_mb, 2) if mem_mb else None,
                "priority": priority
            })

    except Exception as e:
        print(f"Error analyzing running services: {e}")

    return service_info_list


def find_pid_by_service_name(service_name):
    try:
        result = subprocess.run(
            ["systemctl", "show", service_name, "--property=MainPID", "--no-pager"],
            stdout=subprocess.PIPE, text=True
        )
        output = result.stdout.strip()
        if output.startswith("MainPID="):
            pid = int(output.split("=", 1)[1])
            return pid if pid != 0 else None
    except Exception as e:
        print(f"Error finding PID for {service_name}: {e}")
    return None
