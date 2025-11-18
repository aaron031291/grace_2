"""
Citation Formatter - Visual citation formatting for UI
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)

class CitationFormatter:
    """Format citations for visual display in UI"""
    
    def __init__(self):
        self.citation_styles = {
            "academic": self._format_academic,
            "web": self._format_web,
            "compact": self._format_compact,
            "tooltip": self._format_tooltip
        }
    
    def format_citations_for_ui(self, citations: List[Dict[str, Any]], 
                               style: str = "web") -> Dict[str, Any]:
        """Format citations for UI display"""
        formatter = self.citation_styles.get(style, self._format_web)
        
        formatted_citations = []
        citation_map = {}  # For inline citation references
        
        for i, citation in enumerate(citations):
            citation_id = citation.get("id", f"cite_{i+1}")
            
            formatted_citation = {
                "id": citation_id,
                "display_number": i + 1,
                "formatted_text": formatter(citation),
                "confidence_badge": self._create_confidence_badge(citation.get("confidence", 0.8)),
                "verification_badge": self._create_verification_badge(citation.get("verified", False)),
                "interactive_elements": self._create_interactive_elements(citation),
                "metadata": {
                    "source_type": citation.get("source_type", "unknown"),
                    "confidence": citation.get("confidence", 0.8),
                    "verified": citation.get("verified", False),
                    "url": citation.get("url"),
                    "date": citation.get("date")
                }
            }
            
            formatted_citations.append(formatted_citation)
            citation_map[citation_id] = formatted_citation
        
        return {
            "citations": formatted_citations,
            "citation_map": citation_map,
            "total_citations": len(formatted_citations),
            "average_confidence": sum(c.get("confidence", 0.8) for c in citations) / max(len(citations), 1),
            "verified_count": sum(1 for c in citations if c.get("verified", False)),
            "ui_config": {
                "show_confidence_badges": True,
                "show_verification_badges": True,
                "enable_citation_preview": True,
                "citation_style": style
            }
        }
    
    def _format_academic(self, citation: Dict[str, Any]) -> str:
        """Format citation in academic style"""
        author = citation.get("author", "Unknown Author")
        title = citation.get("title", "Unknown Title")
        date = self._format_date(citation.get("date"))
        url = citation.get("url", "")
        
        formatted = f"{author}. \"{title}.\" {date}."
        if url:
            formatted += f" Available at: {url}"
        
        return formatted
    
    def _format_web(self, citation: Dict[str, Any]) -> str:
        """Format citation for web display"""
        title = citation.get("title", "Unknown Source")
        author = citation.get("author")
        date = self._format_date(citation.get("date"))
        url = citation.get("url")
        
        parts = [title]
        if author:
            parts.append(f"by {author}")
        if date:
            parts.append(date)
        
        formatted = " - ".join(parts)
        
        if url:
            formatted = f'<a href="{url}" target="_blank" rel="noopener">{formatted}</a>'
        
        return formatted
    
    def _format_compact(self, citation: Dict[str, Any]) -> str:
        """Format citation in compact style"""
        title = citation.get("title", "Unknown Source")
        if len(title) > 50:
            title = title[:47] + "..."
        
        author = citation.get("author", "").split()[0] if citation.get("author") else ""
        date = self._format_date(citation.get("date"), short=True)
        
        parts = [title]
        if author:
            parts.append(author)
        if date:
            parts.append(date)
        
        return " | ".join(parts)
    
    def _format_tooltip(self, citation: Dict[str, Any]) -> str:
        """Format citation for tooltip display"""
        title = citation.get("title", "Unknown Source")
        excerpt = citation.get("excerpt", "")
        confidence = citation.get("confidence", 0.8)
        verified = citation.get("verified", False)
        
        tooltip = f"**{title}**\n\n"
        if excerpt:
            tooltip += f"{excerpt}\n\n"
        
        tooltip += f"Confidence: {confidence:.1%}\n"
        tooltip += f"Verified: {'✅' if verified else '❌'}"
        
        return tooltip
    
    def _format_date(self, date_str: Optional[str], short: bool = False) -> str:
        """Format date string"""
        if not date_str:
            return "n.d."
        
        try:
            # Parse ISO format
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(date_str)
            
            if short:
                return dt.strftime("%Y")
            else:
                return dt.strftime("%B %d, %Y")
        except:
            # Return as-is if parsing fails
            return date_str[:10] if len(date_str) >= 10 else date_str
    
    def _create_confidence_badge(self, confidence: float) -> Dict[str, Any]:
        """Create confidence badge for UI"""
        if confidence >= 0.9:
            badge_type = "high"
            color = "#22c55e"  # Green
            text = "High Confidence"
        elif confidence >= 0.7:
            badge_type = "medium"
            color = "#f59e0b"  # Yellow
            text = "Medium Confidence"
        else:
            badge_type = "low"
            color = "#ef4444"  # Red
            text = "Low Confidence"
        
        return {
            "type": badge_type,
            "color": color,
            "text": text,
            "percentage": f"{confidence:.1%}",
            "tooltip": f"Confidence score: {confidence:.3f}"
        }
    
    def _create_verification_badge(self, verified: bool) -> Dict[str, Any]:
        """Create verification badge for UI"""
        if verified:
            return {
                "type": "verified",
                "color": "#22c55e",
                "icon": "✅",
                "text": "Verified",
                "tooltip": "This source has been verified"
            }
        else:
            return {
                "type": "unverified",
                "color": "#6b7280",
                "icon": "❓",
                "text": "Unverified",
                "tooltip": "This source has not been verified"
            }
    
    def _create_interactive_elements(self, citation: Dict[str, Any]) -> Dict[str, Any]:
        """Create interactive elements for citation"""
        elements = {
            "preview_available": bool(citation.get("excerpt")),
            "external_link": citation.get("url"),
            "feedback_enabled": True,
            "share_enabled": True
        }
        
        # Add preview content if available
        if citation.get("excerpt"):
            elements["preview_content"] = {
                "excerpt": citation["excerpt"],
                "full_content_available": len(citation.get("content", "")) > 200
            }
        
        return elements
    
    def create_inline_citation_markers(self, text: str, citations: List[Dict[str, Any]]) -> str:
        """Add inline citation markers to text"""
        # This would be enhanced to intelligently place citation markers
        # For now, add citations at the end
        if not citations:
            return text
        
        citation_numbers = [str(i + 1) for i in range(len(citations))]
        citation_marker = "[" + ",".join(citation_numbers) + "]"
        
        return f"{text} {citation_marker}"
    
    def generate_citation_summary(self, citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of citations for UI"""
        if not citations:
            return {
                "total": 0,
                "verified": 0,
                "average_confidence": 0,
                "source_types": {},
                "summary_text": "No citations available"
            }
        
        source_types = {}
        total_confidence = 0
        verified_count = 0
        
        for citation in citations:
            # Count source types
            source_type = citation.get("source_type", "unknown")
            source_types[source_type] = source_types.get(source_type, 0) + 1
            
            # Sum confidence
            total_confidence += citation.get("confidence", 0.8)
            
            # Count verified
            if citation.get("verified", False):
                verified_count += 1
        
        average_confidence = total_confidence / len(citations)
        
        # Generate summary text
        summary_parts = [f"{len(citations)} sources"]
        if verified_count > 0:
            summary_parts.append(f"{verified_count} verified")
        summary_parts.append(f"{average_confidence:.1%} avg confidence")
        
        return {
            "total": len(citations),
            "verified": verified_count,
            "average_confidence": average_confidence,
            "source_types": source_types,
            "summary_text": " • ".join(summary_parts),
            "confidence_distribution": self._calculate_confidence_distribution(citations)
        }
    
    def _calculate_confidence_distribution(self, citations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate confidence score distribution"""
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for citation in citations:
            confidence = citation.get("confidence", 0.8)
            if confidence >= 0.9:
                distribution["high"] += 1
            elif confidence >= 0.7:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1
        
        return distribution

# Global instance
citation_formatter = CitationFormatter()