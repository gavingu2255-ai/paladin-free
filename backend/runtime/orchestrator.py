from .slp.slp import SLP
from .wlm.wlm import WLM
from .knowledge.knowledge import Knowledge
from .persona.persona import PersonaLayer
from .metacog.metacog import Metacog
from .behavior.behavior import BehaviorLayer
from .wgp.wgp import WGP
from .types import ResponseStructure, WLMGraph
from .stp.stp import classify_message
from .llm_client import LLMClient

class RuntimeOrchestrator:
    def __init__(self):
        self.llm = LLMClient()
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
    def detect_slp(self, text: str) -> bool:
        # SLP always runs
        return True

    def detect_wlm(self, text: str) -> bool:
        # WLM always runs
        return True

    def detect_knowledge(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["explain", "what is", "how does", "why does"])

    def detect_persona(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in [
            "act like", "pretend to be", "roleplay as",
            "persona", "speak like", "talk like",
            "mentor", "friendly", "tone"
        ])

    def detect_metacog(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["reflect on", "analyze your reasoning", "think about your answer"])

    def detect_behavior(self, text: str) -> bool:
        # Behavior layer always active
        return True

    def detect_wgp(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["update the world", "change the world state", "modify world"])


    # -----------------------------
    # MAIN PIPELINE
    # -----------------------------
    def run(self, text: str, memory: dict) -> dict:
        print("MEMORY BEFORE:", memory)

        # 1. STP → stance + instruction
        stance_type, instruction = classify_message(text)

        final_prompt = f"""
{instruction}

Input:
"{text}"

Return:
{{
  "advice": "your response"
}}
""".strip()

        print("\n=== FINAL PROMPT TO LLM ===")
        print(final_prompt)
        print("=== END PROMPT ===\n")

        # 2. LLM CALL
        llm_output = self.llm.call(memory, final_prompt)
        memory["llm_output"] = llm_output

        # 3. SLP
        slp_out, _ = self.slp.process(text)
        slp_used = bool(self.detect_slp(text))
        memory["slp_graph"] = slp_out

        # 4. WLM
        if self.detect_wlm(text):
            wlm_out, _ = self.wlm.process(slp_out)
            wlm_out.metadata["raw_text"] = text
            wlm_used = True        # ← INSERTED HERE
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
            wlm_out.metadata["raw_text"] = text
            wlm_used = False


        memory["wlm_graph"] = wlm_out

        # 5. STP
        stp_result = self.run_stp(wlm_out)
        memory["stp"] = stp_result
        print(">>> STP DEBUG:", stp_result)

        # 6. Knowledge
        if self.detect_knowledge(text):
            wlm_out, _ = self.knowledge.process(wlm_out)
            knowledge_used = True
        else:
            knowledge_used = False
        memory["wlm_graph"] = wlm_out

        # 7. Persona
        if self.detect_persona(text):
            wlm_out, _ = self.persona.process(wlm_out)
            persona_used = True
        else:
            persona_used = False
        memory["wlm_graph"] = wlm_out

        # 8. Metacog
        if self.detect_metacog(text) and not self.detect_wgp(text):
            wlm_out, _ = self.metacog.process(wlm_out)
            metacog_used = True
        else:
            metacog_used = False
        memory["wlm_graph"] = wlm_out

        # 9. Behavior
        behavior_plan, behavior_used = self.behavior.process(wlm_out, memory)

        # 10. WGP
        if self.detect_wgp(text) or behavior_plan.act == "world_update":
            wgp_out, _ = self.wgp.evolve_from_input(text, wlm_out, memory)
            wgp_used = True
            memory["world"] = wgp_out
        else:
            wgp_out, wgp_used = None, False

        # 11. FINAL OUTPUT
        content = self.behavior.generate_content(behavior_plan, wlm_out, memory)
        act = behavior_plan.act

        lights = [
            int(bool(slp_used)),
            int(bool(wlm_used)),
            int(bool(persona_used)),
            int(bool(knowledge_used)),
            int(bool(metacog_used)),
            int(bool(behavior_used)),
            int(bool(wgp_used)),
        ]

        response = ResponseStructure(
            content=content,
            graph=wlm_out,
            lights=lights,
            act=act,
        )

        return response.to_dict()
    # -----------------------------
    # STP (modernized topology detector)
    # -----------------------------
    def run_stp(self, wlm_graph):
        raw_text = wlm_graph.metadata.get("raw_text", "").lower()
        entities = wlm_graph.nodes
        tensions = wlm_graph.relations

        # 1. Polarity conflict
        plus_keywords = ["love", "desire", "connection", "relationship"]
        minus_keywords = ["work", "career", "duty", "obligation"]

        plus_hit = any(k in raw_text for k in plus_keywords)
        minus_hit = any(k in raw_text for k in minus_keywords)
        polarity_conflict = plus_hit and minus_hit

        # 2. Tension conflict
        tension_conflict = len(tensions) > 0

        # --- SAFE ENTITY EXTRACTION ---
        entity_list = entities.values() if isinstance(entities, dict) else entities
        
        # 3. Dimensional conflict
        dims = []
        for e in entity_list:
            d = getattr(e, "dimension", None)
            if d is None and isinstance(e, dict):
                d = e.get("dimension")
            if isinstance(d, str) and d.startswith("D"):
                try: dims.append(int(d[1:]))
                except: pass

        dimensional_conflict = (max(dims) - min(dims) > 2) if dims else False

        # 4. Collapse point
        collapse_point = "D3" if any(getattr(e, "dimension", None) == "D3" for e in entity_list) else "D1"

        # 5. Dominant contribution
        dominant = None
        for e in entity_list:
            pol = getattr(e, "polarity", None) if not isinstance(e, dict) else e.get("polarity")
            if pol == "+1":
                # Use 'id' instead of the undefined 'name'
                dominant = getattr(e, "id", "entity_unknown") if not isinstance(e, dict) else e.get("id")
                break

        if not dominant and entity_list:
            try:
                sorted_entities = sorted(
                    entity_list, 
                    key=lambda x: getattr(x, "dimension", "D99") if not isinstance(x, dict) else x.get("dimension", "D99")
                )
                first_e = sorted_entities[0]
                dominant = getattr(first_e, "id", "entity_0") if not isinstance(first_e, dict) else first_e.get("id", "entity_0")
            except:
                dominant = "entity_0"

        # 6. Topology classification
        if polarity_conflict or tension_conflict or dimensional_conflict:
            return {
                "topology": "bifurcation",
                "collapse_risk": True,
                "recommended_axis": "z",
                "conflicts": {
                    "polarity": polarity_conflict,
                    "tension": tension_conflict,
                    "dimension": dimensional_conflict,
                },
                "resolution": {
                    "stable_polarity": "0",
                    "stable_dimension": f"D{min(dims)}" if dims else "D1",
                    "collapse_point": collapse_point,
                    "dominant_contribution": dominant,
                }
            }

        return {
            "topology": "single",
            "collapse_risk": False,
            "recommended_axis": "neutral",
            "conflicts": {
                "polarity": False,
                "tension": False,
                "dimension": False,
            },
            "resolution": {
                "stable_polarity": "0",
                "stable_dimension": "D1",
                "collapse_point": "D1",
                "dominant_contribution": dominant, # Use the identified entity even if single
            }
        }