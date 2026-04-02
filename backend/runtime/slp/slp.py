import uuid
from ..types import Node, Relation, Graph


class SLP:
    def process(self, text: str):
        words = text.split()

        nodes = []
        relations = []

        seen = set()
        for w in words:
            lw = w.lower()
            if lw not in seen:
                seen.add(lw)
                nodes.append(Node(id=str(uuid.uuid4()), label=w))

        if nodes:
            relations.append(Relation(
                source=nodes[0].id,
                target=nodes[-1].id,
                type="mentions"
            ))

        graph = Graph(nodes=nodes, relations=relations)
        used = len(nodes) > 0

        return graph, used
