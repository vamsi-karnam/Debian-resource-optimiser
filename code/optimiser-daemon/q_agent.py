# q_agent.py

import random
import pickle

# Discrete action space
ACTIONS = [
    "do_nothing",
    "suggest_stop_low_priority_service",
    "suggest_renice_heavy_process"
]

class QAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.5):
        self.q_table = {}  # (state_tuple, action) → value
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def discretize_state(self, state):
        """Map raw metrics to a tuple of discrete buckets"""
        mem_bucket = self.bucketize(state["mem_percent"], [30, 60, 85])
        swap_bucket = self.bucketize(state["swap_percent"], [0, 25, 50])
        power_bucket = self.bucketize(state.get("power_watts") or 0, [0.5, 1.5, 3.0])

        return (mem_bucket, swap_bucket, power_bucket)

    def bucketize(self, value, thresholds):
        """Convert a float into a bucket index"""
        for i, t in enumerate(thresholds):
            if value < t:
                return i
        return len(thresholds)

    def choose_action(self, state):
        state_key = self.discretize_state(state)

        if random.random() < self.epsilon:
            return random.choice(ACTIONS)  # explore

        # Get best known action
        q_values = {action: self.q_table.get((state_key, action), 0) for action in ACTIONS}
        return max(q_values, key=q_values.get)

    def update(self, prev_state, action, reward, new_state):
        prev_key = self.discretize_state(prev_state)
        next_key = self.discretize_state(new_state)

        old_value = self.q_table.get((prev_key, action), 0)
        future_rewards = [self.q_table.get((next_key, a), 0) for a in ACTIONS]
        best_future = max(future_rewards)

        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * best_future)
        self.q_table[(prev_key, action)] = new_value

    def save(self, filename="q_table.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)

    def load(self, filename="q_table.pkl"):
        try:
            with open(filename, "rb") as f:
                self.q_table = pickle.load(f)
        except FileNotFoundError:
            self.q_table = {}
