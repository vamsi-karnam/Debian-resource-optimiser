import time
import signal
import sys
from system_monitor import get_system_state
from q_agent import QAgent
from reward import calculate_reward
from action_executor import choose_action, apply_action
from config import LOOP_INTERVAL, ENABLE_POWER_MONITORING
from logger import log_entry

# Optional: power monitoring
if ENABLE_POWER_MONITORING:
    from power_monitor import PowerMonitor
    power_monitor = PowerMonitor()
else:
    power_monitor = None

# Initialize agent and load prior Q-table
agent = QAgent()
agent.load()  

# Graceful exit: save before quitting
def _graceful_exit(signum, frame):
    print("\nSignal received, saving Q-table and exiting…")
    agent.save()
    sys.exit(0)

signal.signal(signal.SIGINT, _graceful_exit)
signal.signal(signal.SIGTERM, _graceful_exit)

previous_state = None
previous_action = None
_last_save = time.time()

while True:
    print("\n[LOOP] Collecting system state...")

    # 1. Collect current state
    state = get_system_state(power_monitor)

    # 2. Choose next action
    action_type = choose_action(state, agent)

    # 3. Apply action and get detail
    action_detail = apply_action(action_type, state)

    # 4. Compute reward and update agent
    if previous_state is not None:
        reward = calculate_reward(state)
        agent.update(previous_state, previous_action["type"], reward, state)
    else:
        reward = None

    # 5. Log the full step
    log_entry(state, action_detail, reward)

    # 6. Save for next iteration
    previous_state = state
    previous_action = action_detail

    # 7. Periodically persist Q-table (every 5 minutes)
    if time.time() - _last_save > 300:
        print("Saving Q-table…")
        agent.save()
        _last_save = time.time()

    time.sleep(LOOP_INTERVAL)
