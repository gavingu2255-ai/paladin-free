from ..types import WLMGraph

ENTITY_TYPES = {
    "i": "person",
    "you": "person",
    "he": "person",
    "she": "person",
    "it": "object",
    "they": "group",
}


class Knowledge:
    def process(self, wlm_graph: WLMGraph):
        # Knowledge should ONLY modify metadata when explicitly triggered.
        before = dict(wlm_graph.metadata)

        # 1. Entity type inference
        for node in wlm_graph.nodes:
            label = node.label.lower()
            if label in ENTITY_TYPES:
                wlm_graph.metadata.setdefault("entity_types", {})
                wlm_graph.metadata["entity_types"][node.id] = ENTITY_TYPES[label]

        # 2. Simple relation inference
        if len(wlm_graph.nodes) >= 2:
            wlm_graph.metadata.setdefault("inferred_relations", [])
            wlm_graph.metadata["inferred_relations"].append("coexist")

        # 3. Mark knowledge as applied
        wlm_graph.metadata["knowledge_applied"] = True

        used = wlm_graph.metadata != before
        return wlm_graph, used
