import json
import os

class StructuralMemory:
    print(">>> USING STRUCTURAL MEMORY FROM:", __file__)

    """
    Stores long-term structural memory for each conversation:
    - world_graph: The 3D+ structural map of the reality.
    - world: High-level world metadata/mood.
    - persona: The active character/style configuration.
    - agent_state: Internal status of the Paladin.
    - workflow: Active task sequences and execution states.
    - file_input: Raw text extracted from system uploads.
    """

    # Allowed keys for structural memory (strict whitelist)
    ALLOWED_KEYS = {
        "world_graph",
        "world",
        "persona",
        "agent_state",
        "workflow",
        "file_input"
    }

    def __init__(self):
        # Base dir: .../paladin-chat/personal_profile
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "personal_profile")
        )
        os.makedirs(base_dir, exist_ok=True)

        self.file_path = os.path.join(base_dir, "paladin_structural_memory.json")
        self.store = {}

        # Load from disk if exists
        self.load_from_file()

    # -----------------------------
    # Persistence
    # -----------------------------
    def save(self):
        """Write ONLY whitelisted structural memory to disk."""
        clean_store = {}

        for cid, mem in self.store.items():
            clean_store[cid] = {
                k: v for k, v in mem.items() if k in self.ALLOWED_KEYS
            }

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(clean_store, f, indent=2)
        except Exception as e:
            print("ERROR saving structural memory:", e)

    def load_from_file(self):
        """Load structural memory from disk if file exists."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.store = json.load(f)
            except Exception as e:
                print("ERROR loading structural memory:", e)
                self.store = {}
        else:
            self.store = {}

    # -----------------------------
    # Core API
    # -----------------------------
    def load(self, cid: str) -> dict:
        """Initialize and return the container for a specific conversation ID."""
        if cid not in self.store:
            self.store[cid] = {
                "world_graph": {"nodes": [], "relations": [], "metadata": {}},
                "world": {},
                "persona": {},
                "agent_state": "idle",
                "workflow": {},
                "file_input": ""
            }
            self.save()
        return self.store[cid]

    def update(self, cid: str, new_graph: dict):
        """Replace ONLY the world_graph."""
        mem = self.load(cid)
        merged_graph = self.merge(mem["world_graph"], new_graph)
        self.store[cid]["world_graph"] = merged_graph
        self.save()

    def merge(self, old: dict, new: dict) -> dict:
        """Full replace — keeps file small."""
        return {
            "nodes": new.get("nodes", []),
            "relations": new.get("relations", []),
            "metadata": new.get("metadata", {}),
        }

    # -----------------------------
    # World
    # -----------------------------
    def get_world(self, cid: str) -> dict:
        return self.load(cid).get("world", {})

    def set_world(self, cid: str, world: dict):
        self.load(cid)["world"] = world
        self.save()

    # -----------------------------
    # Persona
    # -----------------------------
    def get_persona(self, cid: str) -> dict:
        return self.load(cid).get("persona", {})

    def set_persona(self, cid: str, persona: dict):
        self.load(cid)["persona"] = persona
        self.save()

    # -----------------------------
    # Workflow
    # -----------------------------
    def get_workflow(self, cid: str) -> dict:
        return self.load(cid).get("workflow", {})

    def set_workflow(self, cid: str, workflow: dict):
        self.load(cid)["workflow"] = workflow
        self.save()

    # -----------------------------
    # File Input
    # -----------------------------
    def set_file_input(self, cid: str, text: str):
        self.load(cid)["file_input"] = text
        self.save()

    def get_file_input(self, cid: str) -> str:
        return self.load(cid).get("file_input", "")
