from .memory import PersistentMemory

class GraceAutonomous:
    def __init__(self, memory: PersistentMemory):
        self.memory = memory

    async def respond(self, user: str, message: str) -> str:
        normalized = message.lower().strip()
        
        if "hello" in normalized or "hi" in normalized:
            return "Hello! I'm Grace. How can I help you today?"
        
        if "history" in normalized or "remember" in normalized:
            msgs = await self.memory.recent_messages(user, limit=10)
            if not msgs:
                return "We haven't chatted yet. This is our first conversation!"
            history = "\n".join(
                f"{m.role}: {m.content}" for m in msgs[-5:]
            )
            return f"Here are your last interactions:\n{history}"
        
        if "how are you" in normalized:
            return "I'm functioning optimally. All systems operational. How can I assist you?"
        
        if "thank" in normalized:
            return "You're welcome! Happy to help."
        
        if "bye" in normalized or "goodbye" in normalized:
            return "Goodbye! Feel free to return anytime."
        
        return "Thanks for your message. I'm still learning how to help with that. Try asking about your history or saying hello!"
