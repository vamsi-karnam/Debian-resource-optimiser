# Debian-resource-optimiser
A lightweight, self-learning background daemon for Debian that continuously monitors system state (memory, CPU, swap, services, power) and uses tabular Q-learning to suggest (or apply) optimisations - suspending low-priority services and renicing memory-heavy processes - while respecting protected system components and active I/O workloads.

## Key Features

### Adaptive Q-Learning Agent
- Discretizes system metrics into buckets
- ε-greedy exploration with configurable α/γ
- Persists its Q-table across restarts

### Modular Monitoring
- system_monitor.py: RAM, swap, load, top processes
- power_monitor.py: INA219-based power metrics (via Waveshare HAT)

### Smart Action Executor
- Dynamically scans all running systemd services
- Classifies into “protected”, “low-priority”, or “normal”
- Gathers all heavy processes (>5% RAM & low I/O) each loop
- Suggests stopping or renicing multiple targets in a single pass

### Config-Driven Policies
- Centralized config.py for service whitelists, protected lists, thresholds

### Structured Logging
- JSON-L logs of each decision step (logs/log_YYYYMMDD_HHMMSS.jsonl)
- Includes timestamps, full state, action type & targets, and computed reward

### Graceful Shutdown & Persistence
- Handles SIGINT/SIGTERM to save learning before exit
- Periodic auto-save of Q-table ensures continuous improvement


## Getting Started

### Clone & Install
```bash
clone the repo using git clone "https-link"
pip3 install psutil smbus2
```

### Configure
- Edit config.py for your service policies, INA219 I²C address, loop interval

### Run
```bash
Copy
sudo python3 main.py
```

### Analyze Logs & Q-Table
- Logs in logs/ (JSONL)—parse with jq or load into a dashboard
- Q-table saved as q_table.pkl—inspect or reuse in future runs


## Relevant Details
- Threshold Tuning: Adjust memory percentage and I/O limits in config.py or directly in action_executor.py
- Execution Mode: Un-comment systemctl stop and renice calls when you’re ready to automate
- Testing: Use the test script to hog the memory of the device and check if the q-agent can detect the memory usage
