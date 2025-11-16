"""
Unified RAG Prompt & Citation Template

Single source of truth for how Grace formats RAG-augmented prompts.

Used by:
- Remote access API
- MCP integration
- Mission planner
- Chat interfaces
- Unified LLM

This ensures consistent citation format and prompt style across all surfaces.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class RAGPromptTemplate:
    """
    Standard template for RAG-augmented prompts with citations
    
    Provides consistent formatting across Grace's entire system
    """
    
    @staticmethod
    def build_prompt(
        question: str,
        context_chunks: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        mode: str = "conversational",
        system_context: Optional[str] = None
    ) -> str:
        """
        Build a standard RAG prompt with citations
        
        Args:
            question: User's question
            context_chunks: List of context pieces with text
            citations: List of citation metadata
            mode: Prompt style ('conversational', 'technical', 'brief')
            system_context: Optional system-level context
            
        Returns:
            Formatted prompt ready for LLM
        """
        # Build context section with citations
        context_section = RAGPromptTemplate._format_context_with_citations(
            context_chunks,
            citations
        )
        
        # Select style based on mode
        if mode == "conversational":
            style_instruction = """You are Grace, an autonomous AI system. Provide a helpful, conversational response.
Use the provided context to answer accurately, and cite your sources using [1], [2], etc."""
        
        elif mode == "technical":
            style_instruction = """You are Grace, an autonomous AI system. Provide a precise, technical response.
Focus on accuracy and detail. Cite all sources using [1], [2], etc."""
        
        elif mode == "brief":
            style_instruction = """You are Grace, an autonomous AI system. Provide a brief, direct response.
Keep it concise while maintaining accuracy. Cite sources using [1], [2], etc."""
        
        else:
            style_instruction = "Provide an accurate response based on the context. Cite sources using [1], [2], etc."
        
        # Build complete prompt
        prompt_parts = []
        
        if system_context:
            prompt_parts.append(f"System Context: {system_context}\n")
        
        prompt_parts.append(style_instruction)
        prompt_parts.append("\nContext (with citations):")
        prompt_parts.append(context_section)
        prompt_parts.append(f"\nQuestion: {question}")
        prompt_parts.append("\nAnswer (cite your sources):")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def _format_context_with_citations(
        context_chunks: List[Dict[str, Any]],
        citations: List[Dict[str, Any]]
    ) -> str:
        """Format context chunks with citation markers"""
        formatted_chunks = []
        
        for i, chunk in enumerate(context_chunks):
            citation_num = i + 1
            text = chunk.get("text", chunk.get("text_content", ""))
            
            # Add citation marker
            formatted_chunks.append(f"[{citation_num}] {text}")
        
        return "\n\n".join(formatted_chunks)
    
    @staticmethod
    def format_citations(citations: List[Dict[str, Any]]) -> str:
        """
        Format citations for display
        
        Returns formatted citation list for user display
        """
        if not citations:
            return "No citations available."
        
        citation_lines = ["\nSources:"]
        
        for citation in citations:
            num = citation.get("citation_number", "?")
            source_type = citation.get("source_type", "unknown")
            source_id = citation.get("source_id", "")
            score = citation.get("similarity_score", 0.0)
            
            # Format based on source type
            if source_type == "document":
                line = f"[{num}] Document: {source_id} (confidence: {score:.2f})"
            elif source_type == "recording":
                line = f"[{num}] Recording: {source_id} (confidence: {score:.2f})"
            elif source_type == "domain_summary":
                domain = citation.get("metadata", {}).get("domain_id", "unknown")
                line = f"[{num}] {domain} domain knowledge (confidence: {score:.2f})"
            else:
                line = f"[{num}] {source_type}: {source_id} (confidence: {score:.2f})"
            
            citation_lines.append(line)
        
        return "\n".join(citation_lines)
    
    @staticmethod
    def build_response_with_citations(
        answer_text: str,
        citations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Package response with citations in standard format
        
        Returns:
            {
                "answer": str,
                "citations": List[Dict],
                "formatted_citations": str,
                "citation_count": int
            }
        """
        return {
            "answer": answer_text,
            "citations": citations,
            "formatted_citations": RAGPromptTemplate.format_citations(citations),
            "citation_count": len(citations),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def extract_citation_numbers(text: str) -> List[int]:
        """
        Extract citation numbers from text (e.g., [1], [2], [3])
        
        Useful for tracking which sources were actually used in the response
        """
        import re
        matches = re.findall(r'\[(\d+)\]', text)
        return [int(m) for m in matches]
    
    @staticmethod
    def build_system_message(
        role: str = "assistant",
        capabilities: Optional[List[str]] = None
    ) -> str:
        """
        Build standard system message for Grace
        
        Args:
            role: Grace's role context
            capabilities: List of capabilities to mention
            
        Returns:
            System message string
        """
        base_message = "I am Grace, an autonomous AI system with 20 specialized kernels."
        
        if capabilities:
            caps_text = ", ".join(capabilities)
            base_message += f"\n\nMy capabilities include: {caps_text}."
        
        base_message += "\n\nI provide accurate, helpful responses based on my knowledge and cite my sources."
        
        return base_message


# Convenience functions for common use cases

def build_chat_prompt(
    question: str,
    context: Dict[str, Any]
) -> str:
    """
    Build prompt for chat interface
    
    Args:
        question: User question
        context: RAG context with 'context', 'citations'
        
    Returns:
        Formatted prompt
    """
    # Extract chunks from context string
    context_text = context.get("context", "")
    citations = context.get("citations", [])
    
    # Split context into chunks (assuming [1], [2] format)
    import re
    chunks = []
    for match in re.finditer(r'\[(\d+)\]\s*([^\[]+)', context_text):
        chunks.append({"text": match.group(2).strip()})
    
    return RAGPromptTemplate.build_prompt(
        question=question,
        context_chunks=chunks,
        citations=citations,
        mode="conversational"
    )


def build_technical_prompt(
    question: str,
    context: Dict[str, Any],
    domain: Optional[str] = None
) -> str:
    """
    Build prompt for technical/domain-specific queries
    
    Args:
        question: Technical question
        context: RAG context
        domain: Optional domain context
        
    Returns:
        Formatted technical prompt
    """
    context_text = context.get("context", "")
    citations = context.get("citations", [])
    
    import re
    chunks = []
    for match in re.finditer(r'\[(\d+)\]\s*([^\[]+)', context_text):
        chunks.append({"text": match.group(2).strip()})
    
    system_context = f"Domain: {domain}" if domain else None
    
    return RAGPromptTemplate.build_prompt(
        question=question,
        context_chunks=chunks,
        citations=citations,
        mode="technical",
        system_context=system_context
    )


def build_brief_prompt(
    question: str,
    context: Dict[str, Any]
) -> str:
    """
    Build prompt for brief/quick responses
    
    Args:
        question: Question
        context: RAG context
        
    Returns:
        Formatted brief prompt
    """
    context_text = context.get("context", "")
    citations = context.get("citations", [])
    
    import re
    chunks = []
    for match in re.finditer(r'\[(\d+)\]\s*([^\[]+)', context_text):
        chunks.append({"text": match.group(2).strip()})
    
    return RAGPromptTemplate.build_prompt(
        question=question,
        context_chunks=chunks,
        citations=citations,
        mode="brief"
    )


# Global template instance
rag_template = RAGPromptTemplate()