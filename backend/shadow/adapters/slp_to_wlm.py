class SLPtoWLMAdapter:
    """
    Minimal adapter converting SLP graph → WLM graph.
    Shadow Layer does NOT interpret meaning.
    It only renames fields to match WLM expectations.
    """

    def convert(self, slp_graph: dict) -> dict:
        if not slp_graph:
            return {}

        wlm_graph = {}

        for node_id, node in slp_graph.items():
            wlm_graph[node_id] = {
                "type": node.get("type", "entity"),
                "attributes": node.get("attributes", {}),
                "state": node.get("state", {}),
                "spatial": node.get("position", {}),
                "closure": node.get("closure", {})
            }

        return wlm_graph
