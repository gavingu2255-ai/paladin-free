from ..types import WLMGraph, Graph

class WLM:
    def process(self, slp_graph: Graph):
        """
        Minimal WLM:
        - Passes nodes through unchanged
        - Removes meaningless self‑relations
        - Preserves real relations if they exist
        - Adds metadata
        """

        # Filter out self-relations (source == target)
        cleaned_relations = []
        for r in slp_graph.relations:
            if r.source != r.target:
                cleaned_relations.append(r)

        wlm_graph = WLMGraph(
            nodes=slp_graph.nodes,
            relations=cleaned_relations,
            metadata={
                "normalized": True,
                "entity_count": len(slp_graph.nodes),
                "relation_count": len(cleaned_relations),
            }
        )

        used = True
        return wlm_graph, used
