from backend.runtime.orchestrator import RuntimeOrchestrator
from .structural_memory import StructuralMemory
from .full_memory import FullMemory
from .surface_realizer import SurfaceRealizer

print(">>> IMPORTED CHATWRAPPER MODULE:", __file__)
print(">>> IMPORTED STRUCTURAL MEMORY MODULE:", __file__)


class ChatWrapper:
    """
    Shadow Layer entrypoint.
    Provides a stable interface between the Raw Engine (Runtime) 
    and the Frontend/API.
    """

    def __init__(self):
        # The 7-layer engine (SLP -> WLM -> Persona -> Knowledge -> Metacog -> Behavior -> WGP)
        self.runtime = RuntimeOrchestrator()

        # Shadow Layer memory systems
        self.struct_mem = StructuralMemory()  # Graph-based state
        self.full_mem = FullMemory()          # Human-readable logs

        # Expression layer (Structured JSON -> Natural Language)
        self.realizer = SurfaceRealizer()

    def chat(self, text: str, conversation_id: str, api_key: str = None, file_content: str = None) -> dict:
        print(">>> USING CHATWRAPPER FROM:", __file__) 
        """
        Executes the full interaction cycle.
        """

        # 1. Load structural memory
        memory = self.struct_mem.load(conversation_id)
        memory.setdefault("last_act", None)

        # --- TOPIC RESET: prevent workflow contamination ---
        lower = text.lower()

        topic_shift_keywords = [
            "vitamin", "health", "sleep", "doctor", "medicine",
            "supplement", "side effect", "pain", "treatment"
        ]

        if any(k in lower for k in topic_shift_keywords):
            memory["workflow"] = {}
            memory["last_act"] = None
            memory["last_object"] = None
            memory["last_action"] = None


        # --- Minimal Continuity Memory (v1) ---
        memory.setdefault("last_object", None)
        memory.setdefault("last_action", None)

        # ⭐ Ensure token ledger exists
        memory.setdefault("token_usage", {
            "total_input": 0,
            "total_output": 0,
            "history": []
        })

        # If new file content was provided in this specific call, store it first
        if file_content:
            self.struct_mem.set_file_input(conversation_id, file_content)

        # 2. Inject workflow (ONLY if it contains steps)
        existing_workflow = self.struct_mem.get_workflow(conversation_id)
        if existing_workflow and existing_workflow.get("steps"):
            memory["workflow"] = existing_workflow

        # 3. Inject persona, world, file_input
        memory["persona"] = self.struct_mem.get_persona(conversation_id)
        memory["world"] = self.struct_mem.get_world(conversation_id)
        memory["file_input"] = self.struct_mem.get_file_input(conversation_id)

        # ⭐ 4. Inject API key (non-persistent)
        if api_key:
            memory["api_key"] = api_key

        # --- Minimal Continuity Resolver (v1) ---
        clean = text.lower().strip()
        clean = clean.replace(".", "").replace("!", "").replace("?", "")

        VAGUE = [
            "continue", "more", "explain more", "go deeper", "richer",
            "expand", "expand this", "handle this", "fix it", "fix this"
        ]

        if clean in VAGUE and memory.get("last_object"):
            text = f"{memory['last_action']} {memory['last_object']}"


        # 5. Call runtime (7-layer engine)
        result = self.runtime.run(text, memory)
        memory["last_act"] = result.get("act") or result.get("behavior_act")


        # --- Minimal Continuity Extraction (v1) ---
        def extract_last_object_and_action(user_text):
            words = user_text.strip().split()
            if not words:
                return None, None
            action = words[0].lower()
            obj = " ".join(words[1:]).strip() or None
            return action, obj

        action, obj = extract_last_object_and_action(text)

        if action:
            memory["last_action"] = action
        if obj:
            memory["last_object"] = obj

        # --- Clarify Follow-up Shortcut ---
        if memory.get("last_act") == "clarify":
            clarified = text.strip()
            prompt = f"User wants to fix the {clarified} of their schedule. Generate a simple, natural plan."
            reply = self.realizer.generate({"text": prompt})
            return {
                "reply": reply,
                "lights": [0,0,0,0,0,0,1],
                "conversation_id": conversation_id,
                "token_usage": memory.get("token_usage", {})
            }

        # 6. Convert structured content → natural language
        reply = result.get("content", "")

        # Safety: ensure reply is always a string
        if reply is None:
            reply = ""
        else:
            reply = str(reply)

        # 7. Update structural memory with new graph, world, and workflow
        # Graph comes from the direct result
        if "graph" in result:
            self.struct_mem.update(conversation_id, result["graph"])

        # ⭐ CRITICAL FIX: Read 'world' and 'workflow' from the mutated 'memory' bucket
        if "world" in memory and memory["world"]:
            world_data = memory["world"]
            self.struct_mem.set_world(
                conversation_id,
                world_data if isinstance(world_data, dict) else world_data.to_dict()
            )

        # Persist workflow updates (ONLY if workflow contains steps)
        if "workflow" in memory and memory["workflow"].get("steps"):
            self.struct_mem.set_workflow(conversation_id, memory["workflow"])

        # 8. Append to full memory log
        self.full_mem.append(conversation_id, text, reply)

        # 9. Safety Line: Guarantee lights array exists and is valid
        lights = result.get("lights", [0, 0, 0, 0, 0, 0, 0])

        return {
            "reply": reply,
            "lights": lights,
            "conversation_id": conversation_id,
            "token_usage": memory.get("token_usage", {})
            
        }