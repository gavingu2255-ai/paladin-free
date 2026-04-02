import re
from ..types import Graph, WLMGraph


class FileIntelligenceModule:
    """
    Runtime-side File Intelligence.
    Operates on memory["file_input"], memory["world_graph"], memory["world"].
    Does NOT modify Shadow Layer, API, frontend, or orchestrator signature.
    """

    def __init__(self):
        pass

    # ---------- 1. File → Text Processing ----------

    def _clean_text(self, raw: str | None) -> str:
        if not raw:
            return ""
        text = raw.replace("\u00a0", " ")          # non-breaking spaces
        text = re.sub(r"\s+", " ", text)          # collapse whitespace
        text = text.strip()
        return text

    # ---------- 2. Text → SLP Parsing (very minimal) ----------

    def _text_to_slp(self, text: str) -> Graph:
        """
        Very simple SLP:
        - entities: capitalized words
        - relations: 'X knows Y', 'X loves Y'
        """
        nodes = []
        relations = []

        tokens = re.findall(r"\b[A-Z][a-zA-Z]+\b", text)
        seen = {}

        for t in tokens:
            if t not in seen:
                node_id = f"ent_{len(seen)+1}"
                seen[t] = node_id
                nodes.append(type("N", (), {"id": node_id, "label": t})())

        # simple relation patterns
        patterns = [
            (r"(\b[A-Z][a-zA-Z]+\b)\s+knows\s+(\b[A-Z][a-zA-Z]+\b)", "knows"),
            (r"(\b[A-Z][a-zA-Z]+\b)\s+loves\s+(\b[A-Z][a-zA-Z]+\b)", "loves"),
        ]

        for pattern, rel_type in patterns:
            for m in re.finditer(pattern, text):
                src_label, tgt_label = m.group(1), m.group(2)
                if src_label in seen and tgt_label in seen:
                    relations.append(
                        type(
                            "R",
                            (),
                            {
                                "source": seen[src_label],
                                "target": seen[tgt_label],
                                "type": rel_type,
                            },
                        )()
                    )

        return Graph(nodes=nodes, relations=relations)

    # ---------- 3. SLP → WLM Conversion ----------

    def _slp_to_wlm(self, slp_graph: Graph) -> WLMGraph:
        metadata = {
            "source": "file_intel",
            "entity_count": len(slp_graph.nodes),
            "relation_count": len(slp_graph.relations),
        }
        return WLMGraph(
            nodes=slp_graph.nodes,
            relations=slp_graph.relations,
            metadata=metadata,
        )

    # ---------- 4. Merge WLM Into World Graph / World ----------

    def _merge_world_graph(self, existing: dict | None, new_wlm: WLMGraph) -> dict:
        """
        Merge by label: if label already exists, keep existing id and merge relations.
        """
        existing = existing or {"nodes": [], "relations": []}

        label_to_id = {n["label"]: n["id"] for n in existing.get("nodes", [])}
        nodes = list(existing.get("nodes", []))
        relations = list(existing.get("relations", []))

        # merge nodes
        for n in new_wlm.nodes:
            if n.label in label_to_id:
                # already present
                continue
            label_to_id[n.label] = n.id
            nodes.append({"id": n.id, "label": n.label})

        # merge relations (by ids)
        for r in new_wlm.relations:
            rel_dict = {"source": r.source, "target": r.target, "type": r.type}
            if rel_dict not in relations:
                relations.append(rel_dict)

        return {"nodes": nodes, "relations": relations}

    def _merge_world_state(self, existing: dict | None, new_wlm: WLMGraph) -> dict:
        """
        Minimal world merge: add entities as keys with basic attributes.
        """
        existing = existing or {"entities": {}}
        entities = existing.get("entities", {})

        for n in new_wlm.nodes:
            if n.label not in entities:
                entities[n.label] = {
                    "type": "entity",
                    "attributes": {"name": n.label},
                    "state": {},
                    "spatial": {},
                    "closure": {},
                }

        existing["entities"] = entities
        return existing

    # ---------- 5. Public entrypoint for runtime ----------

    def process(self, text: str, memory: dict) -> tuple[dict, WLMGraph | None, dict]:
        """
        Returns:
          updated_memory, new_wlm_graph_or_None, layer_usage_flags
        layer_usage_flags: {"slp_used": bool, "wlm_used": bool, "wgp_used": bool, "metacog_used": bool, "behavior_used": bool}
        """
        raw = memory.get("file_input")
        if not raw:
            return memory, None, {
                "slp_used": False,
                "wlm_used": False,
                "wgp_used": False,
                "metacog_used": False,
                "behavior_used": False,
            }

        clean = self._clean_text(raw)
        slp_graph = self._text_to_slp(clean)
        wlm_graph = self._slp_to_wlm(slp_graph)

        # merge into world_graph and world
        memory["world_graph"] = self._merge_world_graph(memory.get("world_graph"), wlm_graph)
        memory["world"] = self._merge_world_state(memory.get("world"), wlm_graph)

        # optional: you can inspect clean text to trigger workflow/persona on Shadow side

        flags = {
            "slp_used": True,
            "wlm_used": True,
            "wgp_used": True,      # world updated via merge
            "metacog_used": False, # can be flipped when you add checks
            "behavior_used": False,
        }

        return memory, wlm_graph, flags
