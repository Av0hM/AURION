import json
import os

TRAITS_FILE = "memory/traits.json"

DEFAULT_TRAITS = {
    "focus_level": 0.5,
    "stress_prone": 0.5,
    "discipline": 0.5
}

class Learner:
    def __init__(self):
        if not os.path.exists(TRAITS_FILE):
            self.traits = DEFAULT_TRAITS.copy()
            self.save()
        else:
            with open(TRAITS_FILE, "r") as f:
                self.traits = json.load(f)

    def save(self):
        with open(TRAITS_FILE, "w") as f:
            json.dump(self.traits, f, indent=2)

    def learn_from_day(self, day_states):
        total = len(day_states)
        if total == 0:
            return

        focus = day_states.count("DEEP_WORK") + day_states.count("NORMAL_WORK")
        stress = day_states.count("STRESSED") + day_states.count("ANGRY") + day_states.count("CRYING")
        procrast = day_states.count("PROCRASTINATING")

        self.traits["focus_level"] += focus / total
        self.traits["stress_prone"] += stress / total
        self.traits["discipline"] -= procrast / total

        # clamp values
        for k in self.traits:
            self.traits[k] = max(0.0, min(1.0, self.traits[k]))

        self.save()
        print("Learner updated:", self.traits)
