# ============================================================
# STP — Structural Topology Prompting
# Classifies the user message into a stance type
# and returns the appropriate LLM instruction block.
# ============================================================

def classify_message(user_message: str):
    """
    Returns:
        stance_type: str
        llm_instruction: str
    """

    msg = user_message.strip().lower()

    # ---------------------------------------------------------
    # 1. CHOICE QUESTIONS
    # ---------------------------------------------------------
    if is_choice_question(msg):
        if is_meaningful_choice(msg):
            return "meaningful_choice", meaningful_choice_instruction()
        else:
            return "trivial_choice", trivial_choice_instruction()

    # ---------------------------------------------------------
    # 2. EMOTIONAL
    # ---------------------------------------------------------
    if is_emotional(msg):
        return "emotional_vent", emotional_instruction()

    # ---------------------------------------------------------
    # 3. ADVICE / GUIDANCE
    # ---------------------------------------------------------
    if is_advice_request(msg):
        return "practical_guidance", practical_instruction()

    # ---------------------------------------------------------
    # 4. FACTUAL
    # ---------------------------------------------------------
    if is_factual(msg):
        return "factual", factual_instruction()

    # ---------------------------------------------------------
    # 5. REFLECTIVE / EXISTENTIAL
    # ---------------------------------------------------------
    if is_reflective(msg):
        return "reflective", reflective_instruction()

    # ---------------------------------------------------------
    # 6. FALLBACK
    # ---------------------------------------------------------
    return "neutral", neutral_instruction()


# ============================================================
# PATTERN DETECTION HELPERS
# ============================================================

def is_choice_question(msg: str) -> bool:
    return any(phrase in msg for phrase in [
        " or ", " vs ", " versus ", "choose", "pick", "better", "should i"
    ])

def is_meaningful_choice(msg: str) -> bool:
    keywords = [
        # Life-direction
        "love", "relationship", "partner", "family",
        "career", "job", "work", "future", "purpose",
        # Identity / values
        "identity", "values", "freedom", "responsibility",
        # Emotional weight
        "burnout", "stability", "meaning"
    ]
    return any(word in msg for word in keywords)

def is_emotional(msg: str) -> bool:
    return any(phrase in msg for phrase in [
        "i feel", "i'm so", "i am so", "i can't", "i cannot",
        "i'm tired", "i'm overwhelmed", "i'm frustrated",
        "i'm anxious", "i'm scared", "i'm worried"
    ])

def is_advice_request(msg: str) -> bool:
    return any(phrase in msg for phrase in [
        "what should i do", "how do i", "best way", "how should i",
        "give me a plan", "help me with", "how can i"
    ])

def is_factual(msg: str) -> bool:
    return any(phrase in msg for phrase in [
        "what is", "how does", "explain", "define", "why does"
    ])

def is_reflective(msg: str) -> bool:
    return any(phrase in msg for phrase in [
        "why do i", "what's the point", "why is life",
        "why does it matter", "what does it mean"
    ])


# ============================================================
# INSTRUCTION TEMPLATES (MINIMAL + CLEAN)
# ============================================================

def meaningful_choice_instruction() -> str:
    return (
        "All sides matter.\n"
        "User doesn’t have to choose.\n"
        "Help them notice what creates the pressure to choose."
    )

def trivial_choice_instruction() -> str:
    return (
        "Give a short, light response.\n"
        "It's just a preference."
    )

def emotional_instruction() -> str:
    return (
        "Acknowledge their feelings.\n"
        "Keep the response gentle and grounded."
    )

def practical_instruction() -> str:
    return (
        "Give a clear, concrete response.\n"
        "Offer a few grounded suggestions."
    )

def factual_instruction() -> str:
    return (
        "Give a concise, neutral explanation."
    )

def reflective_instruction() -> str:
    return (
        "Offer a thoughtful perspective.\n"
        "Help them explore the deeper meaning."
    )

def neutral_instruction() -> str:
    return (
        "Give a simple, natural response."
    )
