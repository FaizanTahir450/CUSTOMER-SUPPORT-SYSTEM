from langchain.memory import ConversationBufferWindowMemory

class MemoryManager:
    def __init__(self, k=10):
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=k
        )
    
    def get_memory(self):
        return self.memory
    
    def add_message(self, role, content):
        if role == "human":
            self.memory.chat_memory.add_user_message(content)
        else:
            self.memory.chat_memory.add_ai_message(content)
    
    def clear_memory(self):
        self.memory.clear()