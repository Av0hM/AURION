class GoalManager:
    def __init__(self):
        self.goals = {}

    def add_goal(self, name, target_minutes):
        self.goals[name] = {
            "target": target_minutes,
            "progress": 0
        }

    def update_progress(self, state):
        if state in ["DEEP_WORK", "NORMAL_WORK"]:
            for g in self.goals:
                self.goals[g]["progress"] += 1

    def check_completion(self):
        completed = []
        for g, v in self.goals.items():
            if v["progress"] >= v["target"]:
                completed.append(g)
        return completed