from ..types import BehaviorPlan, WLMGraph
from .generator import ContentGenerator
from ..workflow.workflow import WorkflowModule


class BehaviorLayer:
    def __init__(self):
        self.generator = ContentGenerator()
        self.workflow_module = WorkflowModule()

    def process(self, wlm_graph: WLMGraph, memory: dict = None):
        """
        Correct priority order:
        1. Simulation intent → world update / workflow advance
        2. Planning intent → (re)create workflow
        3. Active workflow step → execute step (only if user is continuing)
        4. Persona-biased fallback (NOT counted as behavior)
        """
        memory = memory or {}
        workflow_mem = memory.get("workflow")

        raw_text = (wlm_graph.metadata.get("raw_text") or "").lower()

        # -----------------------------------------
        # PERSONA SWITCH INTENT → short-circuit behavior
        # -----------------------------------------
        persona_triggers = ["switch to", "change to", "set tone to"]
        is_persona_cmd = any(k in raw_text for k in persona_triggers)
        is_tone_spec = "tone" in raw_text and any(
            k in raw_text for k in ["formal", "playful", "neutral", "warm", "cold"]
        )

        if is_persona_cmd or is_tone_spec:
            tone = wlm_graph.metadata.get("persona_tone_modifier", "neutral")
            act = "persona_update"
            steps = [f"System-level intercept: Adjusting persona parameters to {tone}"]
            metadata = {"persona_tone": tone, "short_circuit": True}
            behavior_used = True
            return BehaviorPlan(act=act, steps=steps, metadata=metadata), behavior_used

        # -----------------------------------------
        # SPECIAL CASE: numeric world-evolution steps
        # -----------------------------------------
        import re
        match = re.search(r"(\d+)\s*[\-\u2010-\u2015 ]?\s*steps?", raw_text)
        if match and "world" in raw_text and "evolution" in raw_text:
            count = int(match.group(1))
            act = "world_update"
            steps = [f"simulate {count} world evolution steps"]
            metadata = {
                "simulation": True,
                "count": count,
                "entity_count": wlm_graph.metadata.get("entity_count", 0),
            }
            behavior_used = False
            return BehaviorPlan(act=act, steps=steps, metadata=metadata), behavior_used

        # -----------------------------------------
        # SIMULATION OVERRIDE
        # -----------------------------------------
        if "simulate" in raw_text:
            act = "world_update"
            steps = ["simulate world evolution"]
            metadata = {
                "simulation": True,
                "entity_count": wlm_graph.metadata.get("entity_count", 0),
            }
            behavior_used = False
            return BehaviorPlan(act=act, steps=steps, metadata=metadata), behavior_used

        # -----------------------------------------
        # DOCUMENT MERGE INTENT
        # -----------------------------------------
        if (
            ("merge" in raw_text and "document" in raw_text)
            or ("merge" in raw_text and "documents" in raw_text)
            or ("merge" in raw_text and "file" in raw_text)
            or ("merge" in raw_text and "files" in raw_text)
            or ("summarize" in raw_text and "structure" in raw_text)
            or ("integrate" in raw_text and "world" in raw_text)
        ):
            file_text = memory.get("file_input", "")
            if file_text.strip():
                act = "merge_documents"
                steps = ["parse file_input", "merge into world", "summarize world"]
                metadata = {
                    "file_length": len(file_text),
                    "entity_count": wlm_graph.metadata.get("entity_count", 0),
                    "merge_requested": True,
                }
                behavior_used = True
                memory["file_input"] = ""
                return BehaviorPlan(act=act, steps=steps, metadata=metadata), behavior_used

        # -----------------------------------------
        # KNOWLEDGE QUESTION DETECTION
        # -----------------------------------------
        knowledge_cues = [
            "what is", "what are", "is it true", "does", "do", "can", "should",
            "why", "how", "is vitamin", "is sleep", "is melatonin", "is caffeine"
        ]

        if any(k in raw_text for k in knowledge_cues):
            act = "knowledge"
            steps = ["answer the user's knowledge question clearly and safely"]
            metadata = {"knowledge_query": raw_text}
            behavior_used = True
            return BehaviorPlan(act=act, steps=steps, metadata=metadata), behavior_used

        # -----------------------------------------
        # VAGUE COMMAND DETECTION
        # -----------------------------------------
        entity_count = wlm_graph.metadata.get("entity_count", 0)
        relation_count = wlm_graph.metadata.get("relation_count", 0)

        is_low_structure = (entity_count <= 2 and relation_count == 0)
        has_no_plan_keywords = not any(k in raw_text for k in ["plan", "steps", "workflow"])
        has_no_workflow_cues = not any(
            k in raw_text for k in ["next step", "continue workflow", "step is completed"]
        )
        has_no_simulation_cues = not any(
            k in raw_text for k in ["simulate", "continue the story"]
        )

        # -----------------------------------------
        # 1. PLANNING INTENT (revised)
        # -----------------------------------------
        # Only trigger workflow creation if user explicitly wants a workflow
        explicit_workflow_cues = [
            "workflow",
            "step-by-step workflow",
            "create workflow",
        ]

        if "plan" in raw_text and any(k in raw_text for k in explicit_workflow_cues):
            # User explicitly wants a workflow
            workflow_state = self.workflow_module.plan_from_text(raw_text)
            memory["workflow"] = workflow_state.to_dict()

            steps = [s["text"] for s in workflow_state.steps]
            act = "plan"
            metadata = {
                "entity_count": wlm_graph.metadata.get("entity_count", 0),
                "workflow_created": True,
                "workflow_steps": workflow_state.steps,
            }
            behavior_used = True

        # -----------------------------------------
        # 2. SIMULATION INTENT
        # -----------------------------------------
        elif (
            "continue the story" in raw_text
            or "extend the story" in raw_text
            or "advance the story" in raw_text
            or "integrate into the world" in raw_text
            or "integrate this into the world" in raw_text
            or ("step" in raw_text and "completed" in raw_text)
        ):
            act = "world_update"
            steps = ["simulate world state", "advance workflow if applicable"]
            metadata = {
                "simulation": True,
                "entity_count": wlm_graph.metadata.get("entity_count", 0),
            }
            behavior_used = False

        # -----------------------------------------
        # 3. ACTIVE WORKFLOW STEP / NATURAL ANSWER FALLBACK
        # -----------------------------------------
        else:
            continue_cues = [
                "next step",
                "continue the workflow",
                "continue workflow",
                "go to the next step",
                "expand step",
                "step ",
                "mark step",
                "this step is done",
                "i've completed",
                "i have completed",
                "is completed",
                "step is completed",
                "step 1 is completed",
                "fix my schedule",
                "fix my day",
            ]
            wants_workflow = any(k in raw_text for k in continue_cues)

            wf_behavior = None
            if workflow_mem and wants_workflow:
                wf_behavior = self.workflow_module.behavior_for_current_step(workflow_mem)

            if wf_behavior is not None:
                act = "workflow_step"
                steps = [f"executing workflow step {wf_behavior['step_id']}"]
                metadata = {
                    "workflow_instruction": wf_behavior["instruction"],
                    "step_id": wf_behavior["step_id"],
                    "entity_count": wlm_graph.metadata.get("entity_count", 0),
                }
                behavior_used = True

            else:
                # Treat as a natural request, not a workflow
                act = "answer"
                steps = ["Provide a natural-language answer"]
                metadata = {
                    "fallback": True,
                    "reason": "no active workflow step — defaulting to direct help",
                    "natural_plan": "plan" in raw_text,
                }
                behavior_used = True

        # -----------------------------------------
        # FINAL PLAN RETURN
        # -----------------------------------------
        plan = BehaviorPlan(
            act=act,
            steps=steps,
            metadata=metadata,
        )

        memory["behavior_plan"] = plan.to_dict() if hasattr(plan, "to_dict") else plan
        return plan, behavior_used


    # ============================================================
    # CONTENT GENERATION
    # ============================================================
    def generate_content(self, behavior_plan, wlm_graph, memory):
        """
        If this is a workflow plan, output the actual workflow steps.
        Otherwise, fall back to the persona/content generator.
        """

        # -----------------------------
        # PLAN HANDLING (corrected)
        # -----------------------------
        if behavior_plan.act == "plan":
            llm_advice = memory.get("llm_output", {}).get("advice")

            # CASE 1 — LLM returned a list of steps
            if isinstance(llm_advice, list):
                # Join list items into readable text
                cleaned = "\n".join([f"{i+1}. {step}" for i, step in enumerate(llm_advice)])
                cleaned = cleaned.replace("**Phase", "\n\n**Phase")
                return cleaned

            # CASE 2 — LLM returned a single string
            if isinstance(llm_advice, str):
                cleaned = llm_advice.strip()
                cleaned = cleaned.replace("**Phase", "\n\n**Phase")
                return cleaned

            # CASE 3 — fallback to workflow steps
            steps = behavior_plan.metadata.get("workflow_steps")
            if steps:
                cleaned_steps = []
                import re
                for s in steps:
                    text = s["text"]
                    text = re.sub(r"^\s*Step\s*\d+\s*[:\-]\s*", "", text, flags=re.IGNORECASE)
                    cleaned_steps.append(text)
                return "\n".join([f"{i+1}. {t}" for i, t in enumerate(cleaned_steps)])


        # -----------------------------
        # OTHER ACTS
        # -----------------------------
        if behavior_plan.act == "world_update":
            behavior_plan.text = "Describe the world after evolution."
            return self.generator.generate(behavior_plan, wlm_graph, memory)

        if behavior_plan.act == "merge_documents":
            return "Documents merged into the world model. A structural summary has been generated."

        if behavior_plan.act == "persona_update":
            tone = behavior_plan.metadata.get("persona_tone", "neutral")
            return f"Tone updated to: {tone}."

        if behavior_plan.act == "knowledge":
            return self.generator.generate(behavior_plan, wlm_graph, memory)

        return self.generator.generate(behavior_plan, wlm_graph, memory)


