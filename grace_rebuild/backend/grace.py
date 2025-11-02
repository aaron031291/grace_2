from .memory import PersistentMemory

class GraceAutonomous:
    def __init__(self, memory: PersistentMemory):
        self.memory = memory

    async def respond(self, user: str, message: str) -> str:
        normalized = message.lower().strip()
        
        if "history" in normalized or "remember" in normalized:
            msgs = await self.memory.recent_messages(user, limit=20)
            if len(msgs) < 2:
                return "We just started chatting. Ask me a few more things and then check history again!"
            history = "\n".join(
                f"{m.role.upper()}: {m.content}" for m in msgs[-10:]
            )
            return f"Here are your last {min(len(msgs), 10)} interactions:\n\n{history}"
        
        if "how are you" in normalized:
            return "I'm functioning optimally. All systems operational. How can I assist you?"
        
        if "thank" in normalized:
            return "You're welcome! Happy to help."
        
        if "bye" in normalized or "goodbye" in normalized:
            return "Goodbye! Feel free to return anytime."
        
        return "Thanks for your message. I'm still learning how to help with that. Try asking about your history or saying hello!"
