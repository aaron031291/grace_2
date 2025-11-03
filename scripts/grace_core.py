from sqlalchemy.orm import Session
from models import Message, Task, User
from datetime import datetime
from typing import List, Dict, Optional
import re

class GraceAutonomous:
    def __init__(self, db: Session, user_id: int = 1):
        self.db = db
        self.user_id = user_id
        self.rules = self._load_rules()
    
    def _load_rules(self) -> List[Dict]:
        return [
            {
                "pattern": r"\b(hello|hi|hey)\b",
                "responses": [
                    "Hello! I'm Grace. How can I help you today?",
                    "Hi there! What can I do for you?",
                    "Hey! Ready to assist you."
                ],
                "priority": 1
            },
            {
                "pattern": r"\b(task|todo|remind)\b",
                "responses": [
                    "I can help you manage tasks. Would you like to create, view, or update a task?",
                ],
                "priority": 2,
                "action": "suggest_task_management"
            },
            {
                "pattern": r"\b(create|add|new)\s+(task|todo)\b",
                "responses": [
                    "I'll help you create a task. What should the task title be?",
                ],
                "priority": 3,
                "action": "create_task_flow"
            },
            {
                "pattern": r"\b(show|list|get|view)\s+(task|todo|tasks|todos)\b",
                "responses": [],
                "priority": 3,
                "action": "list_tasks"
            },
            {
                "pattern": r"\b(how are you|how do you feel)\b",
                "responses": [
                    "I'm functioning optimally. All systems operational.",
                    "Running smoothly! How can I assist you?",
                ],
                "priority": 2
            },
            {
                "pattern": r"\b(thank|thanks)\b",
                "responses": [
                    "You're welcome!",
                    "Happy to help!",
                    "Anytime!",
                ],
                "priority": 2
            },
            {
                "pattern": r"\b(bye|goodbye|exit)\b",
                "responses": [
                    "Goodbye! Feel free to reach out anytime.",
                    "See you later!",
                ],
                "priority": 1
            },
        ]
    
    def get_conversation_history(self, limit: int = 10) -> List[Message]:
        return self.db.query(Message).filter(
            Message.user_id == self.user_id
        ).order_by(Message.created_at.desc()).limit(limit).all()
    
    def get_user_tasks(self) -> List[Task]:
        return self.db.query(Task).filter(
            Task.user_id == self.user_id
        ).order_by(Task.created_at.desc()).all()
    
    def _list_tasks_response(self) -> str:
        tasks = self.get_user_tasks()
        if not tasks:
            return "You don't have any tasks yet. Would you like to create one?"
        
        response = f"You have {len(tasks)} task(s):\n\n"
        for task in tasks:
            status_emoji = "✓" if task.status == "completed" else "○"
            response += f"{status_emoji} [{task.id}] {task.title}"
            if task.description:
                response += f" - {task.description}"
            response += f" ({task.status})\n"
        
        return response.strip()
    
    def _analyze_context(self, user_message: str) -> Dict:
        history = self.get_conversation_history(limit=5)
        
        context = {
            "has_history": len(history) > 0,
            "message_count": len(history),
            "recent_topics": [],
            "sentiment": "neutral"
        }
        
        if "!" in user_message:
            context["sentiment"] = "excited"
        elif "?" in user_message:
            context["sentiment"] = "questioning"
        
        return context
    
    def _match_rule(self, user_message: str) -> Optional[Dict]:
        user_message_lower = user_message.lower()
        
        matched_rules = []
        for rule in self.rules:
            if re.search(rule["pattern"], user_message_lower, re.IGNORECASE):
                matched_rules.append(rule)
        
        if matched_rules:
            matched_rules.sort(key=lambda x: x["priority"], reverse=True)
            return matched_rules[0]
        
        return None
    
    def _generate_default_response(self, user_message: str, context: Dict) -> str:
        if "?" in user_message:
            return "I'm not sure I understand that question. I can help you with tasks, reminders, and general conversation. What would you like to do?"
        else:
            return "I hear you. I'm here to help with task management and conversation. What can I do for you?"
    
    def process_message(self, user_message: str, save_to_memory: bool = True) -> str:
        if save_to_memory:
            user_msg = Message(
                user_id=self.user_id,
                content=user_message,
                role="user"
            )
            self.db.add(user_msg)
            self.db.commit()
        
        context = self._analyze_context(user_message)
        
        matched_rule = self._match_rule(user_message)
        
        if matched_rule:
            if matched_rule.get("action") == "list_tasks":
                response = self._list_tasks_response()
            elif matched_rule.get("responses"):
                response = matched_rule["responses"][0]
            else:
                response = self._generate_default_response(user_message, context)
        else:
            response = self._generate_default_response(user_message, context)
        
        if save_to_memory:
            grace_msg = Message(
                user_id=self.user_id,
                content=response,
                role="assistant"
            )
            self.db.add(grace_msg)
            self.db.commit()
        
        return response
    
    def get_metrics(self) -> Dict:
        message_count = self.db.query(Message).filter(
            Message.user_id == self.user_id
        ).count()
        
        task_count = self.db.query(Task).filter(
            Task.user_id == self.user_id
        ).count()
        
        completed_tasks = self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.status == "completed"
        ).count()
        
        return {
            "total_messages": message_count,
            "total_tasks": task_count,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completed_tasks / task_count * 100, 2) if task_count > 0 else 0.0
        }
