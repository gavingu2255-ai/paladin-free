from ..types import WLMGraph


class Metacog:
    def process(self, wlm_graph: WLMGraph):
        """
        Metacog runs only when explicitly triggered by the orchestrator.
        So whenever this is called, we consider Metacog 'used' for lights.
        """
        before = list(wlm_graph.metadata.get("metacog_issues", []))

        issues = []

        # Check 1: empty graph
        if not wlm_graph.nodes:
            issues.append("no_entities")

        # Check 2: relation consistency
        node_ids = {n.id for n in wlm_graph.nodes}
        for rel in wlm_graph.relations:
            if rel.source not in node_ids:
                issues.append("relation_source_missing")
            if rel.target not in node_ids:
                issues.append("relation_target_missing")

        # Check 3: metadata sanity
        if "entity_count" in wlm_graph.metadata:
            if wlm_graph.metadata["entity_count"] != len(wlm_graph.nodes):
                issues.append("entity_count_mismatch")

        wlm_graph.metadata["metacog_issues"] = issues
        wlm_graph.metadata["metacog_checked"] = True

        # Whenever Metacog is invoked by the orchestrator, count it as used
        used = True

        return wlm_graph, used
