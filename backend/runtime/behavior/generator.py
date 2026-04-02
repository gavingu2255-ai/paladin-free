import json

class ContentGenerator:
    def __init__(self):
        pass

    def generate(self, behavior_plan, wlm_graph, memory):
        """
        High-dimensional generator:
        - Persona updates handled deterministically
        - All other acts use LLM output provided by the orchestrator
        - Hybrid mode: STP can still be consulted via memory["stp"]
        """
        act = behavior_plan.act
        raw_text = wlm_graph.metadata.get("raw_text", "")

        # -----------------------------------------
        # 1. Deterministic persona update
        # -----------------------------------------
        if act == "persona_update":
            tone = behavior_plan.metadata.get("persona_tone", "neutral")
            return f"Tone updated to: {tone}."

        # -----------------------------------------
        # 2. Deterministic workflow plan output
        # -----------------------------------------
        if act == "plan":
            steps = behavior_plan.metadata.get("workflow_steps")
            if steps:
                return "\n".join([f"{i+1}. {s['text']}" for i, s in enumerate(steps)])

        # -----------------------------------------
        # 3. Deterministic document merge
        # -----------------------------------------
        if act == "merge_documents":
            return "Documents merged into the world model. A structural summary has been generated."

        # -----------------------------------------
        # 4. LLM OUTPUT (from orchestrator)
        # -----------------------------------------
        llm_response = memory.get("llm_output", {}) or {}

        # STP still available if you want to branch on topology later
        stp = memory.get("stp", {})
        topo = stp.get("topology", "single")

        # Use the LLM's advice field as the human answer
        human_text = llm_response.get("advice", "")

        # CASE 1 — advice is a list (LLM already structured it)
        if isinstance(human_text, list):
            numbered = []
            for i, step in enumerate(human_text, start=1):
                step = step.strip()
                numbered.append(f"{i}. {step}")
            cleaned = "\n\n".join(numbered)   # <-- PARAGRAPH BREAKS
            cleaned = cleaned.replace("**Phase", "\n\n**Phase")
            return cleaned

        # CASE 2 — advice is a string (LLM returned natural text)
        if isinstance(human_text, str) and human_text.strip():
            text = human_text.strip()

            # Split into lines first
            lines = [l.strip() for l in text.split("\n") if l.strip()]

            # If only one line, split into sentences
            if len(lines) <= 1:
                import re
                sentences = re.split(r'(?<=[.!?])\s+', text)
                sentences = [s.strip().rstrip('.') for s in sentences if s.strip()]
                lines = sentences

            # Remove commentary sentences BEFORE numbering
            commentary = [
                "that's a solid approach",
                "great question",
                "sure",
                "absolutely",
                "here's what you can do",
                "you should",
                "i recommend",
            ]

            filtered = []
            for line in lines:
                low = line.lower()
                if any(c in low for c in commentary):
                    continue
                filtered.append(line)

            # If everything was filtered, fall back to original
            if not filtered:
                filtered = lines

            # Number ONLY the filtered steps
            numbered = [f"{i+1}. {step}" for i, step in enumerate(filtered)]


            cleaned = "\n\n".join(numbered)   # <-- PARAGRAPH BREAKS
            cleaned = cleaned.replace("**Phase", "\n\n**Phase")
            return cleaned


        # CASE 3 — fallback to structural
        struct_text = llm_response.get("structural", "")
        if isinstance(struct_text, str) and struct_text.strip():
            return struct_text.strip()

        # -----------------------------------------
        # 5. FALLBACK LOGIC (If LLM output is empty)
        # -----------------------------------------
        if topo == "bifurcation":
            # Placeholder: you can later route to structural resolution here
            pass

        if act == "answer":
            return self._generate_answer(wlm_graph, behavior_plan)
        if act == "reflect":
            return self._generate_reflection(wlm_graph, behavior_plan)
        if act == "generate":
            return self._generate_narrative(wlm_graph)
        if act == "converse":
            return self._generate_conversation(wlm_graph)

        return "Hi — how can I help you today."


    # -----------------------------
    # Helper Methods
    # -----------------------------
    def _resolve_structure(self, interpretation):
        try:
            entities = interpretation.get("entities", {})
            tensions = interpretation.get("tensions", [])
            if isinstance(tensions, dict):
                tensions = list(tensions.values())

            dims = []
            for e in entities.values():
                d = e.get("dimension")
                if isinstance(d, str) and d.startswith("D"):
                    try:
                        dims.append(int(d[1:]))
                    except ValueError:
                        continue

            stable_dimension = f"D{min(dims)}" if dims else "D1"
            collapse_point = "D3" if "D3" in [e.get("dimension") for e in entities.values()] else "D1"

            dominant = None
            for name, e in entities.items():
                if e.get("polarity") == "+1":
                    dominant = name
                    break
            if not dominant and entities:
                dominant = sorted(
                    entities.items(),
                    key=lambda x: x[1].get("dimension", "D99")
                )[0][0]

            return {
                "resolution": {
                    "stable_polarity": "0",
                    "stable_dimension": stable_dimension,
                    "collapse_point": collapse_point,
                    "dominant_contribution": dominant,
                    "structural_path": (
                        f"0 → evaluate → collapse at {collapse_point} "
                        f"→ stabilize at {stable_dimension}"
                    ),
                    "reason": "Resolution computed via STP polarity rules and dimensional collapse."
                }
            }
        except Exception:
            return {"resolution": {"error": "resolution_failed"}}

    def _render_human(self, merged):
        entities = merged.get("entities", {})
        tensions = merged.get("tensions", [])
        resolution = merged.get("resolution", {})

        parts = []

        if entities:
            ent_desc = []
            for name, e in entities.items():
                pol = e.get("polarity")
                dim = e.get("dimension")
                role = e.get("role")
                ent_desc.append(f"{name} ({pol}, {dim}, {role})")
            parts.append("Entities detected: " + ", ".join(ent_desc))

        if tensions:
            t = tensions[0]
            parts.append(
                f"Tension detected between {t.get('entity1')} and {t.get('entity2')}."
            )

        if resolution:
            sp = resolution.get("stable_polarity")
            sd = resolution.get("stable_dimension")
            cp = resolution.get("collapse_point")
            dom = resolution.get("dominant_contribution")

            parts.append(
                f"Structural resolution stabilizes at polarity {sp} in {sd}. "
                f"Collapse occurs at {cp}. "
                f"Dominant contribution: {dom}."
            )

        return " ".join(parts) if parts else "A structural interpretation has been generated."

    def _get_tone_and_verbosity(self, wlm_graph):
        tone = wlm_graph.metadata.get("persona_tone_modifier", "neutral")
        prefs = wlm_graph.metadata.get("persona_preferences", {})
        verbosity = prefs.get("verbosity", "medium")
        return tone, verbosity

    def _generate_answer(self, wlm_graph, behavior_plan):
        count = wlm_graph.metadata.get("entity_count", 0)
        tone, verbosity = self._get_tone_and_verbosity(wlm_graph)

        if tone == "friendly":
            base = f"I noticed {count} entities — happy to help you explore them."
        elif tone == "concise":
            base = f"{count} entities detected."
        elif tone == "formal":
            base = f"The analysis identified {count} distinct entities."
        elif tone == "playful":
            base = f"I spotted {count} little entities running around in your message."
        else:
            base = f"I detected {count} entities."

        if verbosity == "high":
            return base + " I can also walk you through how I derived that."
        if verbosity == "low":
            return base

        return base

    def _generate_reflection(self, wlm_graph, behavior_plan):
        tone, _ = self._get_tone_and_verbosity(wlm_graph)

        if tone == "friendly":
            return "Let me think about that with you for a moment."
        if tone == "concise":
            return "Let me reflect on that briefly."
        if tone == "formal":
            return "Allow me a moment to reflect on the implications."
        if tone == "playful":
            return "Hmm… let me chew on that for a second."

        return "Let me think about that more deeply."

    def _generate_plan(self, behavior_plan):
        steps = behavior_plan.steps or []
        if not steps:
            return "Here is a simple plan to proceed."
        return "Here is the plan I propose:\n- " + "\n- ".join(steps)

    def _generate_narrative(self, wlm_graph):
        count = wlm_graph.metadata.get("entity_count", 0)
        tone, _ = self._get_tone_and_verbosity(wlm_graph)

        if tone == "playful":
            return (
                f"Once upon a prompt, {count} entities woke up and started "
                f"shaping a tiny world."
            )
        return f"There is a world implied by your message, involving about {count} entities."

    def _generate_conversation(self, wlm_graph):
        tone, verbosity = self._get_tone_and_verbosity(wlm_graph)

        if tone == "friendly":
            return "Hi there — what would you like to explore?"
        if tone == "concise":
            return "Hello. How can I help?"
        if tone == "formal":
            return "Hello. How may I assist you today?"
        if tone == "playful":
            return "Hey! What shall we dive into?"

        return "Hi — how can I help you today?"
