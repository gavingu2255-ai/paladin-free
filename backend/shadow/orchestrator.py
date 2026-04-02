from .slp.slp import SLP
from .wlm.wlm import WLM
from .knowledge.knowledge import Knowledge
from .persona.persona import PersonaLayer
from .metacog.metacog import Metacog
from .behavior.behavior import BehaviorLayer
from .wgp.wgp import WGP
from .types import ResponseStructure, WLMGraph


class RuntimeOrchestrator:
    def __init__(self):
        self.slp = SLP()
        self.wlm = WLM()
        self.knowledge = Knowledge()
        self.persona = PersonaLayer()
        self.metacog = Metacog()
        self.behavior = BehaviorLayer()
        self.wgp = WGP()

    # -----------------------------
    # DETECTION FUNCTIONS
    # -----------------------------
    def detect_slp(self, text):
        t = text.lower()
        edit_cues = [
            "place ", "move ", "position", "add ", "remove ", "put ",
            "integrate", "integrate this", "integrate into the world",
            "update the world", "evolve the world",
            "continue the story", "extend the story", "advance the story",
        ]
        return any(k in t for k in edit_cues)

    def detect_wlm(self, text):
        t = text.lower()
        edit_cues = [
            "place ", "move ", "position", "add ", "remove ", "put ",
            "integrate", "integrate this", "integrate into the world",
            "update the world", "evolve the world",
            "continue the story", "extend the story", "advance the story",
        ]
        return any(k in t for k in edit_cues)

    def detect_knowledge(self, text):
        return text.strip().endswith("?")

    def detect_persona(self, text):
        t = text.lower()
        t = t.replace("”", "").replace("“", "").replace("’", "'").replace('"', "").strip()
        persona_cues = [
            "switch to", "change to", "set tone to",
            "formal", "academic", "playful", "neutral",
            "friendly", "professional", "calm", "tone",
            "adopt the style", "adopt this style",
            "match the style", "use the style",
            "writing style", "style of the uploaded file",
        ]
        return any(k in t for k in persona_cues)

    def detect_metacog(self, text):
        metacog_cues = ["why", "explain your reasoning", "how did you", "check your"]
        return any(k in text.lower() for k in metacog_cues)

    def detect_behavior(self, text):
        behavior_cues = ["plan", "steps", "how do i", "what should i do"]
        return any(k in text.lower() for k in behavior_cues)

    def detect_wgp(self, text):
        t = text.lower()
        sim_cues = [
            "simulate", "simulation", "environment", "agent",
            "continue the story", "extend the story", "advance the story",
            "integrate this", "integrate into the world",
            "update the world", "evolve the world",
        ]
        return any(k in t for k in sim_cues)

    # -----------------------------
    # MAIN RUNTIME PIPELINE
    # -----------------------------
    def run(self, text: str, memory: dict) -> dict:
        print("MEMORY BEFORE:", memory)

        # --- Layer 1: SLP ---
        slp_out, _ = self.slp.process(text)
        slp_used = self.detect_slp(text)
        memory["slp_graph"] = slp_out

        # --- Layer 2: WLM ---
        if self.detect_wlm(text):
            wlm_out, wlm_used = self.wlm.process(slp_out)
        else:
            wlm_out = WLMGraph(
                nodes=slp_out.nodes,
                relations=slp_out.relations,
                metadata={
                    "normalized": False,
                    "entity_count": len(slp_out.nodes),
                    "relation_count": len(slp_out.relations),
                },
            )
            wlm_used = False

        wlm_out.metadata["raw_text"] = text
        memory["wlm_graph"] = wlm_out

        # --- Layer 3: Knowledge ---
        if self.detect_knowledge(text):
            wlm_out, knowledge_used = self.knowledge.process(wlm_out)
        else:
            knowledge_used = False

        # --- Layer 4: Persona (EARLY RETURN) ---
        persona_used = self.detect_persona(text)
        if persona_used:
            wlm_out, _ = self.persona.process(wlm_out)
            tone = wlm_out.metadata.get("persona_tone_modifier", "neutral")

            # CRITICAL FIX: Pass wlm_out directly, not .to_dict()
            return ResponseStructure(
                content=f"Persona state updated. System tone set to: {tone}.",
                graph=wlm_out,
                lights=[int(slp_used), int(wlm_used), int(knowledge_used), 1, 0, 0, 0],
                act="persona_update"
            ).to_dict()

        # --- Layer 5: Metacog ---
        if self.detect_metacog(text):
            wlm_out, metacog_used = self.metacog.process(wlm_out)
        else:
            metacog_used = False

        # --- Layer 6: Behavior ---
        behavior_plan, behavior_used = self.behavior.process(wlm_out, memory)

        # --- Layer 7: WGP ---
        if self.detect_wgp(text) or behavior_plan.act == "world_update":
            wgp_out, wgp_used = self.wgp.evolve_from_input(text, wlm_out, memory)
            memory["world"] = wgp_out if isinstance(wgp_out, dict) else wgp_out.to_dict()
        else:
            wgp_used = False

        # --- Content Generation (LLM is called here) ---
        content = self.behavior.generate_content(behavior_plan, wlm_out, memory)

        # --- Final Response ---
        lights = [
            int(slp_used),       # 1 SLP
            int(wlm_used),       # 2 WLM
            int(knowledge_used), # 3 Knowledge
            0,                   # 4 Persona (not used here)
            int(metacog_used),   # 5 Metacog
            int(behavior_used),  # 6 Behavior
            int(wgp_used),       # 7 WGP
        ]

        # CRITICAL FIX: Pass wlm_out directly, not .to_dict()
        return ResponseStructure(
            content=content,
            graph=wlm_out,
            lights=lights,
            act=behavior_plan.act,
        ).to_dict()