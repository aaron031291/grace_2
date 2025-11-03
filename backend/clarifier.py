"""Clarification Module - Constitutional AI Uncertainty Detection

Detects when GRACE is uncertain and generates clarifying questions
before taking potentially incorrect actions.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select

from .models import async_session
from .constitutional_models import ClarificationRequest
from .constitutional_engine import constitutional_engine
from .websocket_manager import WebSocketManager

class Clarifier:
    """Detect uncertainty and request clarification from users"""
    
    def __init__(self):
        # Confidence thresholds
        self.clarification_threshold = 0.7  # Below this, ask for clarification
        self.high_confidence = 0.9  # Above this, no clarification needed
        
        # Uncertainty patterns
        self.ambiguous_pronouns = ['it', 'that', 'this', 'they', 'them', 'those', 'these']
        self.vague_terms = ['better', 'fix', 'improve', 'optimize', 'clean up', 'refactor']
        
    async def analyze_and_clarify(
        self,
        user: str,
        user_input: str,
        context: Dict[str, Any],
        confidence: float = 1.0,
        action_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze input for uncertainty and request clarification if needed
        
        Args:
            user: Username
            user_input: User's original input
            context: Current context
            confidence: GRACE's confidence in interpretation (0.0-1.0)
            action_type: Type of action being considered
        
        Returns:
            Clarification request if needed, None if confident
        """
        
        # Check if confidence is too low
        if confidence < self.clarification_threshold:
            uncertainty_type = "low_confidence"
            question = await self._generate_low_confidence_question(user_input, context, confidence)
            
        else:
            # Check for other uncertainty types
            uncertainty = self.detect_uncertainty(user_input, context)
            
            if not uncertainty:
                return None  # No clarification needed
            
            uncertainty_type = uncertainty['type']
            question = uncertainty['question']
        
        # Create clarification request
        clarification = await constitutional_engine.request_clarification(
            user=user,
            original_input=user_input,
            uncertainty_type=uncertainty_type,
            confidence=confidence,
            question=question,
            options=uncertainty.get('options') if 'uncertainty' in locals() else None,
            context=uncertainty.get('context') if 'uncertainty' in locals() else None,
            timeout_minutes=60
        )
        
        # Notify user via WebSocket
        try:
            ws_manager = WebSocketManager()
            await ws_manager.send_to_user(
                user=user,
                message_type="clarification_request",
                data={
                    "request_id": clarification['request_id'],
                    "question": question,
                    "options": clarification.get('options'),
                    "context": clarification.get('context'),
                    "confidence": confidence,
                    "uncertainty_type": uncertainty_type
                }
            )
        except Exception as e:
            print(f"Failed to send clarification WebSocket: {e}")
        
        return clarification
    
    def detect_uncertainty(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Detect various types of uncertainty in user input
        
        Returns:
            Uncertainty details or None if confident
        """
        
        # 1. Check for ambiguous pronouns
        ambiguity = self._check_ambiguous_pronouns(user_input, context)
        if ambiguity:
            return ambiguity
        
        # 2. Check for missing parameters
        missing = self._check_missing_parameters(user_input, context)
        if missing:
            return missing
        
        # 3. Check for conflicting instructions
        conflict = self._check_conflicting_instructions(user_input, context)
        if conflict:
            return conflict
        
        # 4. Check for vague requirements
        vague = self._check_vague_requirements(user_input, context)
        if vague:
            return vague
        
        # 5. Check for policy violations that might be intentional
        policy = self._check_policy_ambiguity(user_input, context)
        if policy:
            return policy
        
        return None
    
    def _check_ambiguous_pronouns(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check for ambiguous pronoun references"""
        
        input_lower = user_input.lower()
        
        # Check for pronouns
        for pronoun in self.ambiguous_pronouns:
            pattern = rf'\b{pronoun}\b'
            if re.search(pattern, input_lower):
                # Check if context provides clear referent
                recent_entities = context.get('recent_entities', [])
                
                if len(recent_entities) > 1:
                    # Multiple possible referents
                    return {
                        'type': 'ambiguous_pronoun',
                        'question': f"When you say '{pronoun}', which do you mean?",
                        'options': recent_entities[:5],  # Limit to 5 options
                        'context': f"I see multiple possibilities: {', '.join(recent_entities[:5])}"
                    }
                elif len(recent_entities) == 0:
                    # No clear referent
                    return {
                        'type': 'ambiguous_pronoun',
                        'question': f"What does '{pronoun}' refer to?",
                        'context': "I don't have enough context to understand what you're referring to."
                    }
        
        return None
    
    def _check_missing_parameters(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check for commands missing required parameters"""
        
        input_lower = user_input.lower()
        
        # Common commands requiring parameters
        commands = {
            'fix': 'Which issue or bug should I fix?',
            'delete': 'What should I delete?',
            'update': 'What should I update?',
            'change': 'What should I change?',
            'add': 'What should I add?',
            'remove': 'What should I remove?',
        }
        
        for cmd, question in commands.items():
            if cmd in input_lower:
                # Check if specific target is mentioned
                has_target = any([
                    re.search(r'\b(file|function|class|variable|bug|issue|test)\b', input_lower),
                    re.search(r'["\'][\w\s]+["\']', user_input),  # Quoted text
                    context.get('current_file'),
                    context.get('selected_text')
                ])
                
                if not has_target:
                    # Get context options
                    options = []
                    if context.get('open_files'):
                        options.extend([f"file: {f}" for f in context['open_files'][:5]])
                    if context.get('recent_issues'):
                        options.extend([f"issue: {i}" for i in context['recent_issues'][:5]])
                    
                    return {
                        'type': 'missing_parameter',
                        'question': question,
                        'options': options if options else None,
                        'context': f"Your command '{cmd}' needs a specific target."
                    }
        
        return None
    
    def _check_conflicting_instructions(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check for contradictory instructions"""
        
        # Common conflicts
        conflicts = [
            (['fast', 'quick'], ['thorough', 'comprehensive'], "speed vs thoroughness"),
            (['simple', 'minimal'], ['feature-rich', 'complete'], "simplicity vs features"),
            (['safe', 'secure'], ['experimental', 'cutting-edge'], "safety vs innovation"),
        ]
        
        input_lower = user_input.lower()
        
        for group1, group2, conflict_type in conflicts:
            has_group1 = any(term in input_lower for term in group1)
            has_group2 = any(term in input_lower for term in group2)
            
            if has_group1 and has_group2:
                return {
                    'type': 'conflicting_instruction',
                    'question': f"I see conflicting requirements regarding {conflict_type}. Which is more important?",
                    'options': [
                        f"Prioritize {group1[0]}",
                        f"Prioritize {group2[0]}",
                        "Balance both"
                    ],
                    'context': f"Your request mentions both {group1} and {group2}."
                }
        
        return None
    
    def _check_vague_requirements(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check for vague or subjective requirements"""
        
        input_lower = user_input.lower()
        
        # Vague terms that need clarification
        vague_patterns = {
            r'\bbetter\b': "What specific aspect should be improved?",
            r'\bimprove\b': "How should I improve it?",
            r'\boptimize\b': "What should I optimize for? (speed, memory, readability)",
            r'\bclean\s+up\b': "What needs cleaning? (formatting, unused code, structure)",
            r'\brefactor\b': "What's the goal of the refactor?",
            r'\bmake\s+it\s+work\b': "What's not working? What should the behavior be?",
        }
        
        for pattern, question in vague_patterns.items():
            if re.search(pattern, input_lower):
                return {
                    'type': 'vague_requirement',
                    'question': question,
                    'context': "This is subjective and could be interpreted multiple ways."
                }
        
        return None
    
    def _check_policy_ambiguity(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check if request might violate policy but could be intentional"""
        
        input_lower = user_input.lower()
        
        # Potentially risky patterns
        risky_patterns = {
            r'delete\s+all': "Delete ALL items? This is irreversible.",
            r'drop\s+(database|table)': "Drop the database/table? All data will be lost.",
            r'force\s+push': "Force push will overwrite remote history. Are you sure?",
            r'chmod\s+777': "chmod 777 is insecure. Do you really want this?",
            r'disable\s+(security|auth)': "Disable security? This creates vulnerabilities.",
        }
        
        for pattern, warning in risky_patterns.items():
            if re.search(pattern, input_lower):
                return {
                    'type': 'policy_violation',
                    'question': warning,
                    'options': [
                        "Yes, proceed anyway",
                        "No, suggest safer alternative",
                        "Explain why this is risky"
                    ],
                    'context': "This action could be risky or violate best practices."
                }
        
        return None
    
    async def _generate_low_confidence_question(
        self,
        user_input: str,
        context: Dict[str, Any],
        confidence: float
    ) -> str:
        """Generate question when confidence is low"""
        
        confidence_pct = int(confidence * 100)
        
        return (
            f"I'm only {confidence_pct}% confident I understand what you want. "
            f"Could you clarify or rephrase? "
            f"Specifically: what's the goal, and what should the outcome look like?"
        )
    
    async def get_pending_clarifications(self, user: str) -> List[Dict[str, Any]]:
        """Get all pending clarification requests for a user"""
        
        async with async_session() as session:
            result = await session.execute(
                select(ClarificationRequest).where(
                    ClarificationRequest.user == user,
                    ClarificationRequest.status == "pending",
                    ClarificationRequest.timeout_at > datetime.utcnow()
                )
            )
            requests = result.scalars().all()
            
            return [
                {
                    'request_id': req.request_id,
                    'question': req.question,
                    'options': req.options,
                    'context': req.context_provided,
                    'original_input': req.original_input,
                    'created_at': req.created_at.isoformat(),
                    'timeout_at': req.timeout_at.isoformat()
                }
                for req in requests
            ]
    
    async def handle_timeout(self, request_id: str) -> Dict[str, Any]:
        """Handle clarification request timeout - take safe default action"""
        
        async with async_session() as session:
            result = await session.execute(
                select(ClarificationRequest).where(
                    ClarificationRequest.request_id == request_id
                )
            )
            request = result.scalar_one_or_none()
            
            if not request or request.status != "pending":
                return {"status": "not_found"}
            
            # Mark as timeout
            request.status = "timeout"
            request.responded_at = datetime.utcnow()
            
            await session.commit()
            
            return {
                'status': 'timeout',
                'default_action': 'no_action',
                'message': 'Clarification timed out. No action taken for safety.'
            }

clarifier = Clarifier()
