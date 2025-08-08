# reward.py

def calculate_reward(state):
    """
    Compute a reward based on the current system state.

    Higher is better. The agent will try to maximize this reward over time.
    """

    mem_penalty = state["mem_percent"]               # higher % = worse
    swap_penalty = state["swap_percent"] * 2         # higher swap is much worse
    cpu_penalty = state["cpu_load_1min"] * 1.5       # discourage high CPU load

    # Optional: power usage penalty (if power data is available)
    if state["power_watts"] is not None:
        power_penalty = state["power_watts"] * 5     # weight power usage heavily
    else:
        power_penalty = 0

    # Base reward is the inverse of total penalty
    reward = 100 - (mem_penalty + swap_penalty + cpu_penalty + power_penalty)

    return round(reward, 2)
