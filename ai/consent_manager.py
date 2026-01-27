class ConsentManager:
    def __init__(self):
        self.overrides = {}

    def disable(self, state):
        self.overrides[state] = True

    def enable(self, state):
        self.overrides[state] = False

    def is_allowed(self, state):
        return not self.overrides.get(state, False)
