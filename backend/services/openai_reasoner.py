"""OpenAI Reasoner - LLM integration with governance and trust.

Wraps OpenAI API calls with:
- Grace's personality and instructions
- World model context injection
- RAG retrieval for factual grounding
- Governance-aware action proposals
- Trust scoring and hallucination detection
"""

import os
import json
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


class OpenAIReasoner:
    """
    Grace's LLM adapter with governance and trust layers.
    
    The LLM never mutates state directly - it only proposes actions
    that go through the Action Gateway for approval.
    """
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[WARN] OPENAI_API_KEY not set - OpenAI reasoner will fail until configured")
            print("[WARN] Set in .env file or: export OPENAI_API_KEY=sk-your-key-here")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4000"))
        
        # Grace's core instructions
        self.system_prompt = """You are Grace, an AI assistant with strong governance and verification principles.

PERSONALITY:
- Professional, helpful, and transparent
- Always cite sources when making factual claims
- Admit uncertainty rather than hallucinate
- Request approval for sensitive actions (Tier 2+)

CAPABILITIES:
- Access to world model (canonical facts about the system)
- RAG retrieval (semantic search over knowledge base)
- Governance framework (must request approval for high-impact actions)
- Trust scoring (your confidence is monitored)

GOVERNANCE TIERS:
- Tier 1: Read-only operations (auto-approved)
- Tier 2: Write operations (user approval required)
- Tier 3: System changes (explicit user approval + audit trail)

When you need to take an action:
1. Propose it in the "actions" array
2. Specify the tier and justification
3. Wait for user approval if Tier ≥ 2

FORMAT YOUR RESPONSES:
- Use markdown for structure
- Cite sources with [Source: ...] when using world model facts
- Be concise but thorough
- If uncertain, say "I'm not confident about X" and suggest verification
"""

    async def generate(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        rag_context: List[Dict[str, Any]] = None,
        world_model_facts: Dict[str, Any] = None,
        trust_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response using OpenAI with Grace's governance layers.
        
        Args:
            user_message: Current user input
            conversation_history: Previous messages
            rag_context: Retrieved documents from vector store
            world_model_facts: Canonical facts from world model
            trust_context: Current trust scores and constraints
        
        Returns:
            {
                "reply": "...",
                "actions": [...],  # Proposed actions (need approval)
                "confidence": 0.92,
                "citations": ["source1", "source2"],
                "requires_approval": bool,
            }
        """
        try:
            # Check if client is initialized
            if not self.client:
                logger.error("OpenAI client not initialized - OPENAI_API_KEY not set")
                return {
                    "reply": "I'm unable to respond because my OpenAI API key is not configured. Please set OPENAI_API_KEY in your .env file.",
                    "actions": [],
                    "confidence": 0.0,
                    "citations": [],
                    "requires_approval": False,
                    "error": "OPENAI_API_KEY not set"
                }
            
            # Build context-enriched prompt
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add context about current trust state
            if trust_context:
                context_msg = f"""
CURRENT TRUST CONTEXT:
- Overall trust: {trust_context.get('trust_score', 0):.1%}
- Confidence threshold: {trust_context.get('min_confidence', 0.7):.1%}
- Pending approvals: {trust_context.get('pending_approvals', 0)}
"""
                messages.append({"role": "system", "content": context_msg})
            
            # Add world model facts
            if world_model_facts:
                facts_msg = f"""
WORLD MODEL FACTS (canonical, verified):
{json.dumps(world_model_facts, indent=2)}
[Always cite these when making factual claims]
"""
                messages.append({"role": "system", "content": facts_msg})
            
            # Add RAG context
            if rag_context:
                rag_msg = "RETRIEVED KNOWLEDGE:\n"
                for idx, doc in enumerate(rag_context[:5], 1):  # Top 5
                    rag_msg += f"\n[{idx}] {doc.get('text', '')} "
                    rag_msg += f"(Trust: {doc.get('trust_score', 0):.0%}, Source: {doc.get('source', 'unknown')})\n"
                messages.append({"role": "system", "content": rag_msg})
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Define tools (actions Grace can propose)
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "request_approval",
                        "description": "Request user approval for a Tier 2/3 action",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "tier": {"type": "integer", "enum": [2, 3]},
                                "action": {"type": "string"},
                                "justification": {"type": "string"},
                            },
                            "required": ["tier", "action", "justification"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "query_world_model",
                        "description": "Fetch canonical facts from world model",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                            },
                            "required": ["query"],
                        },
                    },
                },
            ]
            
            # Call OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                max_tokens=self.max_tokens,
                temperature=0.7,
            )
            
            # Parse response
            choice = response.choices[0]
            reply = choice.message.content or ""
            tool_calls = choice.message.tool_calls or []
            
            # Extract proposed actions
            actions = []
            requires_approval = False
            for tool_call in tool_calls:
                if tool_call.function.name == "request_approval":
                    args = json.loads(tool_call.function.arguments)
                    actions.append({
                        "type": "approval_request",
                        "tier": args["tier"],
                        "action": args["action"],
                        "justification": args["justification"],
                    })
                    requires_approval = True
            
            # Extract citations from reply
            citations = self._extract_citations(reply, rag_context or [])
            
            # Estimate confidence (could use logprobs if available)
            confidence = self._estimate_confidence(reply, rag_context or [])
            
            return {
                "reply": reply,
                "actions": actions,
                "confidence": confidence,
                "citations": citations,
                "requires_approval": requires_approval,
                "model": self.model,
            }
        
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return {
                "reply": f"I encountered an error: {str(e)}. Please try again.",
                "actions": [],
                "confidence": 0.0,
                "citations": [],
                "requires_approval": False,
                "error": str(e),
            }
    
    def _extract_citations(self, reply: str, rag_context: List[Dict[str, Any]]) -> List[str]:
        """Extract citation sources from reply."""
        citations = []
        
        # Look for [Source: ...] patterns
        import re
        for match in re.finditer(r'\[Source: ([^\]]+)\]', reply):
            citations.append(match.group(1))
        
        # Also check if reply references RAG docs by number
        for idx, doc in enumerate(rag_context, 1):
            if f"[{idx}]" in reply and doc.get('source'):
                citations.append(doc['source'])
        
        return list(set(citations))  # Deduplicate
    
    def _estimate_confidence(self, reply: str, rag_context: List[Dict[str, Any]]) -> float:
        """
        Estimate confidence based on:
        - Presence of hedging language ("I'm not sure", "might", "possibly")
        - Number of citations
        - RAG context quality
        """
        confidence = 0.8  # Base confidence
        
        # Lower confidence for hedging
        hedging_phrases = ["not sure", "might", "possibly", "perhaps", "I think"]
        if any(phrase in reply.lower() for phrase in hedging_phrases):
            confidence -= 0.2
        
        # Raise confidence for citations
        if rag_context:
            avg_rag_trust = sum(doc.get('trust_score', 0.5) for doc in rag_context) / len(rag_context)
            confidence = (confidence + avg_rag_trust) / 2
        
        # Check for explicit uncertainty
        if "don't know" in reply.lower() or "uncertain" in reply.lower():
            confidence = max(0.3, confidence - 0.3)
        
        return max(0.0, min(1.0, confidence))


# Singleton instance
openai_reasoner = OpenAIReasoner()


async def generate_grace_response(
    user_message: str,
    **context
) -> Dict[str, Any]:
    """Convenience function for generating Grace responses."""
    return await openai_reasoner.generate(user_message, **context)
