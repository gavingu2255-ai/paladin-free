class Node:
    def __init__(self, id: str, label: str):
        self.id = id
        self.label = label


class Relation:
    def __init__(self, source: str, target: str, type: str):
        self.source = source
        self.target = target
        self.type = type


class Graph:
    def __init__(self, nodes=None, relations=None):
        self.nodes = nodes or []
        self.relations = relations or []

    def to_dict(self):
        return {
            "nodes": [vars(n) for n in self.nodes],
            "relations": [vars(r) for r in self.relations],
        }


class WLMGraph(Graph):
    def __init__(self, nodes=None, relations=None, metadata=None):
        super().__init__(nodes=nodes, relations=relations)
        self.metadata = metadata or {}

    def to_dict(self):
        base = super().to_dict()
        base["metadata"] = self.metadata
        return base


class Persona:
    def __init__(
        self,
        id: str,
        name: str,
        style: str = "",
        tone: str = "",
        preferences: dict | None = None,
    ):
        self.id = id
        self.name = name
        self.style = style
        self.tone = tone
        self.preferences = preferences or {}

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "style": self.style,
            "tone": self.tone,
            "preferences": self.preferences,
        }


class BehaviorPlan:
    def __init__(
        self,
        act: str,
        steps: list[str] | None = None,
        metadata: dict | None = None,
        text: str = "",
    ):
        self.act = act
        self.steps = steps or []
        self.metadata = metadata or {}
        self.text = text

    def to_dict(self):
        return {
            "act": self.act,
            "steps": self.steps,
            "metadata": self.metadata,
            "text": self.text,
        }


class ResponseStructure:
    def __init__(self, content: str, graph: Graph, lights: list[int], act: str):
        self.content = content
        self.graph = graph
        self.lights = lights
        self.act = act

    def to_dict(self):
        return {
            "content": self.content,
            "graph": self.graph.to_dict() if hasattr(self.graph, "to_dict") else self.graph,
            "lights": self.lights,
            "act": self.act,
        }
