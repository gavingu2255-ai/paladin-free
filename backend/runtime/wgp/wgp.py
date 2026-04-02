from ..types import WLMGraph

class WorldState:
    """
    Data Structure for the simulated world state.
    Acts as the 'Physical Anchor' for the WGP layer.
    """
    def __init__(self, entities=None, time_step: int = 0, weather: str = "clear"):
        # entities: {"bird": {"location": "tree", "mood": "curious"}, ...}
        self.entities = entities or {}   
        self.time_step = time_step
        self.weather = weather

    def to_dict(self):
        """Converts object to dictionary for Shadow Layer persistence."""
        return {
            "entities": self.entities,
            "time_step": self.time_step,
            "weather": self.weather,
        }

    @classmethod
    def from_dict(cls, data: dict | None):
        """Creates a WorldState object from stored memory."""
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
    Operates on memory["world"], persona, workflow, and WLMGraph.
    """

    def __init__(self):
        pass

    # ---------- 1. Main entry for world updates ----------

    def evolve_from_input(self, text: str, wlm_graph: WLMGraph, memory: dict) -> tuple[dict, bool]:
        """
        Main entry point. Returns (new_world_dict, used_flag).
        The 'used' flag determines if Light 7 (WGP) activates.
        """
        # Hydrate current state from memory
        world_state = WorldState.from_dict(memory.get("world"))
        persona = memory.get("persona", {}) or {}
        workflow = memory.get("workflow", {}) or {}

        text_lower = text.lower().strip()

        # Detect numeric simulation: e.g., "simulate 20 steps"
        import re
        match = re.search(r"(\d+)\s*[\-\u2010-\u2015 ]?\s*steps?", text_lower)
        if match:
            step_count = int(match.group(1))
        else:
            step_count = 1

        # Check for explicit advancement commands
        advance_triggers = [
            "advance the world",
            "simulate",
            "what happens next",
            "continue the story",
            "evolve the world"
            "world evolution", 
            "steps of world evolution" 
        ]

        if any(cmd in text_lower for cmd in advance_triggers):
            # ⭐ FIX: actually run multiple steps
            for _ in range(step_count):
                self._advance_world(world_state, persona, workflow)
            return world_state.to_dict(), True

        # Otherwise: narrative update
        used = self._apply_narrative_update(text_lower, world_state, persona, workflow)
        return world_state.to_dict(), used

    # ---------- 2. Temporal World Advancement ----------

    def _advance_world(self, world_state: WorldState, persona: dict, workflow: dict):
        """Advances the world clock and applies persona/workflow 'drift'."""
        world_state.time_step += 1

        # Simple weather cycle: change weather every 3 steps
        if world_state.time_step % 3 == 0:
            world_state.weather = "cloudy" if world_state.weather == "clear" else "clear"

        # Persona-biased shaping: Identitiy influences the 'vibe' of the world
        tone = persona.get("tone") or persona.get("persona_tone_modifier")
        if tone in ["warm", "friendly", "playful"]:
            for ent in world_state.entities.values():
                if isinstance(ent, dict) and "mood" in ent:
                    ent["mood"] = "hopeful"

        # Workflow influence: Automatically generates scenes if a task is active
        if workflow and not world_state.entities:
            world_state.entities["scene"] = {
                "description": "A stable environment forming around the task context.",
                "status": "manifested"
            }

    # ---------- 3. Specific Narrative Updates ----------

    def _apply_narrative_update(self, text_lower: str, world_state: WorldState, persona: dict, workflow: dict) -> bool:
        """Interprets text to see if the user manually shifted a world variable."""
        used = False

        # Example: "the bird flies away"
        if "bird" in text_lower and "flies" in text_lower:
            bird = world_state.entities.get("bird", {})
            bird["location"] = "sky"
            bird["mood"] = bird.get("mood", "curious")
            world_state.entities["bird"] = bird
            world_state.time_step += 1
            used = True

        # Example: "it starts raining"
        if "rain" in text_lower or "raining" in text_lower:
            world_state.weather = "rainy"
            world_state.time_step += 1
            used = True

        # Persona bias: Analytical personas add 'last_updated' metadata to entities
        style = persona.get("style")
        if used and style == "analytical":
            for name, ent in world_state.entities.items():
                if isinstance(ent, dict):
                    ent["step_log"] = world_state.time_step
                    world_state.entities[name] = ent

        return used
    
