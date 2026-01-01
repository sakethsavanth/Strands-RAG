class ConversationMemory:
    def __init__(self, max_turns=6):
        self.history = []
        self.max_turns = max_turns

    def add(self, query, answer):
        self.history.append({
            "query": query,
            "answer": answer
        })
        self.history = self.history[-self.max_turns:]

    def get(self):
        return self.history
