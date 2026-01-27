from .ai_analyzer import analyze_frame
from .memory import StateMemory
from .learner import UserProfile
from .persona_router import route_persona
from .intent_inference import infer_intent
from .predictor import predict_next
from .goal_manager import GoalManager
from .consent_manager import ConsentManager
from .ethics import ethical_filter

memory = StateMemory()
profile = UserProfile()
goals = GoalManager()
consent = ConsentManager()

def decide(state, intensity, intent, prediction):
    if state == "CRYING":
        return "IMMEDIATE_COMFORT"
    if state == "ANGRY":
        return "DE_ESCALATE"
    if intensity > 0.7 and state in ["STRESSED", "TIRED"]:
        return "INTERVENE"
    if intent == "avoidance":
        return "MOTIVATE"
    if state == "DEEP_WORK":
        return "DO_NOT_DISTURB"
    return "OBSERVE"

def cognitive_engine(image):
    perception = analyze_frame(image)
    state = perception["state"]
    intensity = perception["intensity"]

    memory.add(state)
    profile.update_traits(state)

    recent_states = memory.last_n(5)

    MACRO_MAP = {
    "DEEP_WORK": "WORKING",
    "NORMAL_WORK": "WORKING",
    "DISTRACTED": "IDLE",
    "PROCRASTINATING": "IDLE",
    "BORED": "IDLE",
    "AWAY": "IDLE",
    "TIRED": "NEGATIVE",
    "STRESSED": "NEGATIVE",
    "ANGRY": "NEGATIVE",
    "CRYING": "NEGATIVE",
    "EATING": "PHYSICAL",
    "VICTORY": "POSITIVE"
    }

    macro_state = MACRO_MAP.get(state, "UNKNOWN")

    persona = route_persona(state)
    intent = infer_intent(state, macro_state, intensity, recent_states)
    prediction = predict_next(memory)
    goals.update_progress(state)

    decision = decide(state, intensity, intent, prediction)

    if not consent.is_allowed(state):
        decision = "DO_NOTHING"

    decision = ethical_filter(state, intent, decision)

    return {
        "state": state,
        "intensity": intensity,
        "persona": persona,
        "intent": intent,
        "prediction": prediction,
        "decision": decision
    }