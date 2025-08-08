# system_monitor.py

import psutil
import subprocess

def get_system_state(power_monitor=None):
    state = {}

    # Memory usage
    mem = psutil.virtual_memory()
    state["mem_total_mb"] = round(mem.total / (1024 * 1024), 2)
    state["mem_used_mb"] = round(mem.used / (1024 * 1024), 2)
    state["mem_free_mb"] = round(mem.available / (1024 * 1024), 2)
    state["mem_percent"] = mem.percent

    # Swap usage
    swap = psutil.swap_memory()
    state["swap_used_mb"] = round(swap.used / (1024 * 1024), 2)
    state["swap_percent"] = swap.percent

    # CPU load
    load1, load5, load15 = psutil.getloadavg()
    state["cpu_load_1min"] = load1
    state["cpu_load_5min"] = load5
    state["cpu_load_15min"] = load15

    # Top 3 memory-using processes
    processes = sorted(psutil.process_iter(['pid', 'name', 'memory_info']),
                       key=lambda p: p.info['memory_info'].rss,
                       reverse=True)[:3]
    state["top_processes"] = [
        {"pid": p.info['pid'], "name": p.info['name'],
         "mem_mb": round(p.info['memory_info'].rss / (1024 * 1024), 2)}
        for p in processes
    ]

    # Optional power metrics (if enabled)
    if power_monitor:
        power_data = power_monitor.get_power_state()
        state.update({
            "power_voltage": power_data["voltage"],
            "power_current": power_data["current"],
            "power_watts": power_data["power"]
        })
    else:
        state.update({
            "power_voltage": None,
            "power_current": None,
            "power_watts": None
        })

    return state
