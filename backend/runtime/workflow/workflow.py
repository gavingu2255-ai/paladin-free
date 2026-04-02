from ..types import WLMGraph
import re


class WorkflowState:
    def __init__(self, steps=None, current_step=1, completed=False):
        self.steps = steps or []
        self.current_step = current_step
        self.completed = completed

    def to_dict(self):
        return {
            "steps": self.steps,
            "current_step": self.current_step,
            "completed": self.completed,
        }


class WorkflowModule:
    """
    Runtime-side workflow planner and executor.
    Works only with memory["workflow"], does not touch Shadow Layer.
    """

    def __init__(self):
        pass

    # ============================================================
    # 1. PLANNER
    # ============================================================

    def plan_from_text(self, text: str) -> WorkflowState:
        text_lower = text.lower()

        # -----------------------------------------
        # 0. Extract explicit step count (e.g., "20-step", "20 steps")
        # -----------------------------------------
        match = re.search(r"(\d+)\s*[\-\u2010-\u2015 ]?\s*step", text_lower)
        if match:
            step_count = int(match.group(1))
        else:
            step_count = None

        # -----------------------------------------
        # 1. Workspace organization planner
        # -----------------------------------------
        if "workspace" in text_lower or "desk" in text_lower:
            steps = [
                {"id": 1, "text": "Clear the workspace", "status": "pending"},
                {"id": 2, "text": "Sort items by category", "status": "pending"},
                {"id": 3, "text": "Organize tools and supplies", "status": "pending"},
                {"id": 4, "text": "Clean surfaces", "status": "pending"},
                {"id": 5, "text": "Establish a maintenance routine", "status": "pending"},
            ]

        # -----------------------------------------
        # 2. Blog post planner
        # -----------------------------------------
        elif "blog post" in text_lower:
            steps = [
                {"id": 1, "text": "Choose a topic", "status": "pending"},
                {"id": 2, "text": "Write outline", "status": "pending"},
                {"id": 3, "text": "Draft sections", "status": "pending"},
                {"id": 4, "text": "Edit and refine", "status": "pending"},
            ]

        # -----------------------------------------
        # 3. Generic numeric planner (NEW)
        # -----------------------------------------
        elif step_count is not None:
            steps = []
            for i in range(step_count):
                steps.append({
                    "id": i + 1,
                    "text": f"Step {i+1}: part of the plan for {text_lower}",
                    "status": "pending"
                })

        # -----------------------------------------
        # 4. Generic fallback
        # -----------------------------------------
        else:
            steps = [
                {"id": 1, "text": "Clarify the goal", "status": "pending"},
                {"id": 2, "text": "Break the goal into steps", "status": "pending"},
                {"id": 3, "text": "Execute the first step", "status": "pending"},
            ]

        return WorkflowState(steps=steps, current_step=1, completed=False)

    # ============================================================
    # 2. STATE UPDATES
    # ============================================================

    def update_from_command(self, workflow: dict | None, command: str) -> WorkflowState:
        state = self._from_dict(workflow)
        cmd = command.lower().strip()

        # Natural-language: "step 1 is completed", "complete step 2", etc.
        if "step" in cmd and ("complete" in cmd or "done" in cmd or "finish" in cmd):
            try:
                step_id = int([w for w in cmd.split() if w.isdigit()][0])
                self._move_to(state, step_id)
                self._mark_current_done(state)
                self._advance(state)
            except Exception:
                pass

        # Simple commands
        elif cmd in ["next", "continue"]:
            self._advance(state)

        elif cmd in ["done", "complete"]:
            self._mark_current_done(state)
            self._advance(state)

        elif cmd.startswith("move to step"):
            try:
                step_id = int(cmd.split()[-1])
                self._move_to(state, step_id)
            except ValueError:
                pass

        elif cmd in ["skip", "skip this"]:
            self._skip_current(state)

        self._recompute_completed(state)
        return state

    # ============================================================
    # 3. BEHAVIOR PLAN HOOK
    # ============================================================

    def behavior_for_current_step(self, workflow: dict | None) -> dict | None:
        state = self._from_dict(workflow)

        if not state.steps or state.completed:
            return None

        step = next((s for s in state.steps if s["id"] == state.current_step), None)
        if not step:
            return None

        return {
            "act": "workflow_step",
            "step_id": step["id"],
            "instruction": step["text"],
        }

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    def _from_dict(self, data: dict | None) -> WorkflowState:
        if not data:
            return WorkflowState()
        return WorkflowState(
            steps=data.get("steps", []),
            current_step=data.get("current_step", 1),
            completed=data.get("completed", False),
        )

    def _advance(self, state: WorkflowState):
        ids = [s["id"] for s in state.steps]
        if not ids:
            return
        try:
            idx = ids.index(state.current_step)
        except ValueError:
            return
        if idx + 1 < len(ids):
            state.current_step = ids[idx + 1]

    def _move_to(self, state: WorkflowState, step_id: int):
        ids = [s["id"] for s in state.steps]
        if step_id in ids:
            state.current_step = step_id

    def _mark_current_done(self, state: WorkflowState):
        for s in state.steps:
            if s["id"] == state.current_step:
                s["status"] = "done"

    def _skip_current(self, state: WorkflowState):
        for s in state.steps:
            if s["id"] == state.current_step:
                s["status"] = "skipped"

    def _recompute_completed(self, state: WorkflowState):
        if not state.steps:
            state.completed = False
            return
        state.completed = all(
            s["status"] in ["done", "skipped"] for s in state.steps
        )
