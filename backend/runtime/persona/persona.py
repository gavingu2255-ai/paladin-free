from ..types import Persona, WLMGraph

# ---- Persona presets ----

PERSONA_PRESETS = {
    "paladin": Persona(
        id="paladin",
        name="Paladin",
        style="direct",
        tone="warm",
        preferences={"verbosity": "medium", "emphasis": "clarity"},
    ),
    "sage": Persona(
        id="sage",
        name="Sage",
        style="reflective",
        tone="warm",
        preferences={"verbosity": "high", "emphasis": "reasoning"},
    ),
    "scout": Persona(
        id="scout",
        name="Scout",
        style="direct",
        tone="cold",
        preferences={"verbosity": "low", "emphasis": "speed"},
    ),
}


class PersonaLayer:
    def __init__(self, default_persona: Persona | None = None, preset_id: str | None = None):
        # Priority: explicit persona > preset > hardcoded default
        if default_persona is not None:
            self.current_persona = default_persona
        elif preset_id is not None and preset_id in PERSONA_PRESETS:
            self.current_persona = PERSONA_PRESETS[preset_id]
        else:
            self.current_persona = Persona(
                id="default",
                name="Paladin",
                style="direct",
                tone="warm",
                preferences={"verbosity": "medium"},
            )

    def process(self, wlm_graph: WLMGraph):
        """
        Detect tone commands, update persona, and attach persona metadata.
        Supports multi-tone messages (last tone wins).
        """
        before = dict(wlm_graph.metadata)

        # --- 1. Normalize text ---
        raw = wlm_graph.metadata.get("raw_text", "").lower()
        t = raw.replace("”", "").replace("“", "").replace("’", "'").strip()

        # --- 2. Multi-tone detection (last tone wins) ---
        tones = []

        if "formal" in t and "academic" in t:
            tones.append("formal")
        if "playful" in t:
            tones.append("playful")
        if "neutral" in t:
            tones.append("neutral")
        if "warm" in t:
            tones.append("warm")
        if "cold" in t:
            tones.append("cold")

        detected_tone = tones[-1] if tones else None

        # --- 3. Update persona tone if detected ---
        if detected_tone:
            self.current_persona.tone = detected_tone

        persona = self.current_persona

        # --- 4. Attach persona metadata ---
        wlm_graph.metadata["persona"] = persona.to_dict()

        # --- 5. Tone → response style modifier ---
        tone = persona.tone
        if tone == "warm":
            wlm_graph.metadata["persona_tone_modifier"] = "friendly"
        elif tone == "cold":
            wlm_graph.metadata["persona_tone_modifier"] = "concise"
        elif tone == "formal":
            wlm_graph.metadata["persona_tone_modifier"] = "formal"
        elif tone == "playful":
            wlm_graph.metadata["persona_tone_modifier"] = "playful"
        else:
            wlm_graph.metadata["persona_tone_modifier"] = "neutral"

        # --- 6. Style → behavior bias ---
        style = persona.style
        if style == "direct":
            wlm_graph.metadata["persona_behavior_bias"] = "answer"
        elif style == "reflective":
            wlm_graph.metadata["persona_behavior_bias"] = "reflect"
        elif style == "analytical":
            wlm_graph.metadata["persona_behavior_bias"] = "plan"
        elif style == "narrative":
            wlm_graph.metadata["persona_behavior_bias"] = "generate"
        else:
            wlm_graph.metadata["persona_behavior_bias"] = "answer"

        # --- 7. Preferences ---
        wlm_graph.metadata["persona_preferences"] = persona.preferences

        used = wlm_graph.metadata != before
        return wlm_graph, used

    # Runtime-side editing API (does not touch orchestrator)
    def set_persona_by_id(self, preset_id: str):
        if preset_id in PERSONA_PRESETS:
            self.current_persona = PERSONA_PRESETS[preset_id]

    def update_persona(self, **kwargs):
        # Simple editing: override fields and preferences
        if "style" in kwargs:
            self.current_persona.style = kwargs["style"]
        if "tone" in kwargs:
            self.current_persona.tone = kwargs["tone"]
        if "preferences" in kwargs and isinstance(kwargs["preferences"], dict):
            self.current_persona.preferences.update(kwargs["preferences"])
