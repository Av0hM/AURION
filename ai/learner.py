class Learner:
    def __init__(self):
        self.traits = {
            "focus": 0.5,
            "discipline": 0.5,
            "stress": 0.5
        }

    def learn_from_day(self, day_states):
        if not day_states:
            return

        total = len(day_states)

        focus = sum(1 for s in day_states if s["state"] in ["FOCUSED", "DEEP_WORK"])
        stress = sum(1 for s in day_states if s["state"] in ["STRESSED", "ANGRY", "TIRED"])
        procrast = sum(1 for s in day_states if s["state"] == "PROCRASTINATING")

        self.traits["focus"] += focus / total
        self.traits["stress"] += stress / total
        self.traits["discipline"] -= procrast / total

        # clamp
        for k in self.traits:
            self.traits[k] = max(0.0, min(1.0, self.traits[k]))

        print("Learner updated:", self.traits)