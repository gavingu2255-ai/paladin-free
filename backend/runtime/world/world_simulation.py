from ..types import WLMGraph

class WorldState:
    """
    Data Structure for the simulated world state.
    """
    def __init__(self, entities=None, time_step: int = 0, weather: str = "clear"):
        self.entities = entities or {}   # e.g., {"bird": {"location": "tree", "mood": "curious"}}
        self.time_step = time_step
        self.weather = weather

    def to_dict(self):
        return {
            "entities": self.entities,
            "time_step": self.time_step,
            "weather": self.weather,
        }

    @classmethod
    def from_dict(cls, data: dict | None):
        if not data:
            return cls()
        return cls(
            entities=data.get("entities", {}),
            time_step=data.get("time_step", 0),
            weather=data.get("weather", "clear"),
        )

class WGP:
    """
    Runtime-side world simulation engine.
    Processes narrative updates and temporal advancement.
    """

    def __init__(self):
        pass

    # ---------- 1. Main entry for world updates ----------

    def evolve_from_input(self, text: str, wlm_graph: WLMGraph, memory: dict) -> tuple[dict, bool]:
        """
        Processes input text and returns (new_world_dict, used_flag).
        """
        world_state = WorldState.from_dict(memory.get("world"))
        persona = memory.get("persona", {}) or {}
        workflow = memory.get("workflow", {}) or {}

        text_lower = text.lower().strip()

        # Check for explicit advancement commands
        advance_cmds = ["advance the world", "simulate", "what happens next", "continue the story", "evolve the world"]
        if any(cmd in text_lower for cmd in advance_cmds):
            self._advance_world(world_state, persona, workflow)
            used = True
        else:
            # Check for specific narrative triggers (e.g., "it starts raining")
            used = self._apply_narrative_update(text_lower, world_state, persona, workflow)

        return world_state.to_dict(), used

    # ---------- 2. Temporal World Advancement ----------

    def _advance_world(self, world_state: WorldState, persona: dict, workflow: dict):
        world_state.time_step += 1

        # Periodic weather drift
        if world_state.time_step % 3 == 0:
            world_state.weather = "cloudy" if world_state.weather == "clear" else "clear"

        # Persona-biased shaping: Personalities influence the 'vibe' of the world
        tone = persona.get("tone") or persona.get("persona_tone_modifier")
        if tone in ["warm", "friendly", "playful"]:
            for ent in world_state.entities.values():
                if "mood" in ent:
                    ent["mood"] = "hopeful"

        # Workflow influence: creates context-aware scenes
        if workflow and not world_state.entities:
            world_state.entities["scene"] = {"description": "A setting forming around the task context."}

    # ---------- 3. Specific Narrative Updates ----------

    def _apply_narrative_update(self, text_lower: str, world_state: WorldState, persona: dict, workflow: dict) -> bool:
        used = False

        # Example trigger: "the bird flies away"
        if "bird" in text_lower and "flies" in text_lower:
            bird = world_state.entities.get("bird", {})
            bird["location"] = "sky"
            bird["mood"] = bird.get("mood", "curious")
            world_state.entities["bird"] = bird
            world_state.time_step += 1
            used = True

        # Example trigger: "it starts raining"
        if "rain" in text_lower or "raining" in text_lower:
            world_state.weather = "rainy"
            world_state.time_step += 1
            used = True

        # Persona bias: Analytical styles add structured tracking to entities
        style = persona.get("style")
        if used and style == "analytical":
            for name, ent in world_state.entities.items():
                ent.setdefault("last_updated_step", world_state.time_step)
                world_state.entities[name] = ent

        return used