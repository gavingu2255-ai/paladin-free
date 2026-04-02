class FullMemory:
    """
    Stores full conversation logs.
    Does not affect reasoning.
    """

    def __init__(self):
        self.logs = {}

    def append(self, cid: str, user: str, assistant: str):
        if cid not in self.logs:
            self.logs[cid] = []
        self.logs[cid].append({
            "user": user,
            "assistant": assistant
        })

    def load_all(self, cid: str):
        return self.logs.get(cid, [])
