from collections import deque, Counter
import json

class StateMemory:
    def __init__(self, max_len=25):
        self.states = deque(maxlen=max_len)

    def add(self, state):
        self.states.append(state)

    def last_n(self, n=5):
        return list(self.states)[-n:]

    def frequency(self):
        return Counter(self.states)

    def dominant(self):
        if not self.states:
            return None
        return self.frequency().most_common(1)[0][0]

    def trend(self, state, threshold=3):
        return self.last_n(5).count(state) >= threshold

    def save(self, path="data/memory.json"):
        with open(path, "w") as f:
            json.dump(list(self.states), f)

    def load(self, path="data/memory.json"):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                self.states.extend(data)
        except:
            pass
