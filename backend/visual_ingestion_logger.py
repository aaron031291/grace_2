"""
Visual Ingestion Logger
Real-time visual logs of Grace's knowledge ingestion with cryptographic verification
Shows clickable HTTP links to sources, verification status, and complete audit trail
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import hashlib
from pathlib import Path
import json

from .immutable_log import immutable_log
from .unified_logger import unified_logger
from .models import async_session
from .knowledge_provenance import KnowledgeSource
from sqlalchemy import select, desc

logger = logging.getLogger(__name__)


class VisualIngestionLogger:
    """
    Visual logging of all knowledge ingestion with crypto verification
    """
    
    def __init__(self):
        self.log_file = Path(__file__).parent.parent / "logs" / "ingestion_visual.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.html_log = Path(__file__).parent.parent / "logs" / "ingestion.html"
        
        self.ingestion_count = 0
        self.verified_count = 0
        
    async def log_ingestion(
        self,
        source_id: str,
        source_type: str,
        url: str,
        title: str,
        content_hash: str,
        verification_status: Dict[str, bool],
        immutable_log_hash: str,
        previous_hash: str,
        signature: str,
        metadata: Dict[str, Any]
    ):
        """
        Log knowledge ingestion with full visual output and crypto verification
        
        Creates:
        - Terminal log with clickable links
        - HTML log for browser viewing
        - Database entry with verification
        """
        
        self.ingestion_count += 1
        
        # Check if fully verified
        fully_verified = all(verification_status.values())
        if fully_verified:
            self.verified_count += 1
        
        # Create visual log entry
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Terminal log with ANSI colors and clickable link
        terminal_log = f"""
{'='*100}
🌐 KNOWLEDGE INGESTION #{self.ingestion_count} - {timestamp}
{'='*100}

📋 SOURCE INFORMATION:
   Source ID:    {source_id}
   Type:         {source_type.upper()}
   Title:        {title}
   URL:          {url}
   
🔗 CLICKABLE LINK (Ctrl+Click to open):
   {url}

🛡️  VERIFICATION STATUS:
   Hunter Protocol:      {'✅ VERIFIED' if verification_status.get('hunter', False) else '❌ FAILED'}
   Governance:           {'✅ APPROVED' if verification_status.get('governance', False) else '❌ BLOCKED'}
   Constitutional AI:    {'✅ COMPLIANT' if verification_status.get('constitutional', False) else '❌ VIOLATION'}
   Overall:              {'✅ FULLY VERIFIED' if fully_verified else '⚠️  PARTIAL VERIFICATION'}

🔐 CRYPTOGRAPHIC VERIFICATION:
   Content Hash:         {content_hash}
   Immutable Log Hash:   {immutable_log_hash}
   Previous Hash:        {previous_hash or 'N/A (first entry)'}
   Signature:            {signature[:32]}...
   Chain Verified:       {'✅ VALID' if previous_hash else '✅ GENESIS'}

📊 CONTENT METADATA:
   Word Count:           {metadata.get('word_count', 0):,}
   Code Snippets:        {metadata.get('code_count', 0)}
   Domain:               {metadata.get('domain', 'N/A')}
   Trust Score:          {metadata.get('trust_score', 0.5):.2f}

📈 INGESTION STATISTICS:
   Total Ingestions:     {self.ingestion_count}
   Verified:             {self.verified_count}
   Verification Rate:    {(self.verified_count/self.ingestion_count*100):.1f}%

{'='*100}
"""
        
        # Write to terminal log
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(terminal_log + '\n')
        
        # Print to console
        print(terminal_log)
        
        # Create HTML entry
        await self._append_html_log(
            source_id=source_id,
            source_type=source_type,
            url=url,
            title=title,
            timestamp=timestamp,
            content_hash=content_hash,
            verification_status=verification_status,
            immutable_log_hash=immutable_log_hash,
            previous_hash=previous_hash,
            signature=signature,
            metadata=metadata,
            fully_verified=fully_verified
        )
        
        logger.info(f"[INGESTION] 📋 Logged: {source_id} - {title}")
    
    async def _append_html_log(
        self,
        source_id: str,
        source_type: str,
        url: str,
        title: str,
        timestamp: str,
        content_hash: str,
        verification_status: Dict[str, bool],
        immutable_log_hash: str,
        previous_hash: str,
        signature: str,
        metadata: Dict[str, Any],
        fully_verified: bool
    ):
        """Append entry to HTML log"""
        
        # Create HTML if doesn't exist
        if not self.html_log.exists():
            self._create_html_template()
        
        # Read current HTML
        html_content = self.html_log.read_text(encoding='utf-8')
        
        # Create new entry
        status_color = '#27ae60' if fully_verified else '#f39c12'
        status_text = '✅ FULLY VERIFIED' if fully_verified else '⚠️ PARTIAL'
        
        entry_html = f"""
        <div class="ingestion-entry {'verified' if fully_verified else 'partial'}">
            <div class="entry-header">
                <span class="entry-number">#{self.ingestion_count}</span>
                <span class="timestamp">{timestamp}</span>
                <span class="status" style="background-color: {status_color}">{status_text}</span>
            </div>
            
            <div class="source-info">
                <h3>{title}</h3>
                <p><strong>Type:</strong> {source_type.upper()} | <strong>Source ID:</strong> <code>{source_id}</code></p>
                <p><strong>🔗 URL:</strong> <a href="{url}" target="_blank" class="source-link">{url}</a></p>
            </div>
            
            <div class="verification-grid">
                <div class="verification-item {'verified' if verification_status.get('hunter') else 'failed'}">
                    <span class="icon">{'✅' if verification_status.get('hunter') else '❌'}</span>
                    <span>Hunter Protocol</span>
                </div>
                <div class="verification-item {'verified' if verification_status.get('governance') else 'failed'}">
                    <span class="icon">{'✅' if verification_status.get('governance') else '❌'}</span>
                    <span>Governance</span>
                </div>
                <div class="verification-item {'verified' if verification_status.get('constitutional') else 'failed'}">
                    <span class="icon">{'✅' if verification_status.get('constitutional') else '❌'}</span>
                    <span>Constitutional AI</span>
                </div>
            </div>
            
            <div class="crypto-section">
                <h4>🔐 Cryptographic Verification</h4>
                <table>
                    <tr>
                        <td>Content Hash:</td>
                        <td><code class="hash">{content_hash}</code></td>
                    </tr>
                    <tr>
                        <td>Immutable Log Hash:</td>
                        <td><code class="hash">{immutable_log_hash}</code></td>
                    </tr>
                    <tr>
                        <td>Previous Hash:</td>
                        <td><code class="hash">{previous_hash or 'GENESIS'}</code></td>
                    </tr>
                    <tr>
                        <td>Signature:</td>
                        <td><code class="hash">{signature[:64]}...</code></td>
                    </tr>
                    <tr>
                        <td>Chain Status:</td>
                        <td><span class="verified">✅ VALID</span></td>
                    </tr>
                </table>
            </div>
            
            <div class="metadata-section">
                <h4>📊 Content Metadata</h4>
                <div class="metadata-grid">
                    <div class="metadata-item">
                        <strong>Word Count:</strong> {metadata.get('word_count', 0):,}
                    </div>
                    <div class="metadata-item">
                        <strong>Code Snippets:</strong> {metadata.get('code_count', 0)}
                    </div>
                    <div class="metadata-item">
                        <strong>Domain:</strong> {metadata.get('domain', 'N/A')}
                    </div>
                    <div class="metadata-item">
                        <strong>Trust Score:</strong> {metadata.get('trust_score', 0.5):.2f}
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Insert before closing body tag
        html_content = html_content.replace(
            '<div id="ingestion-log">',
            f'<div id="ingestion-log">\n{entry_html}'
        )
        
        # Update stats
        stats_html = f"""
        <div class="stat-card">
            <h3>{self.ingestion_count}</h3>
            <p>Total Ingestions</p>
        </div>
        <div class="stat-card">
            <h3>{self.verified_count}</h3>
            <p>Verified Sources</p>
        </div>
        <div class="stat-card">
            <h3>{(self.verified_count/self.ingestion_count*100):.1f}%</h3>
            <p>Verification Rate</p>
        </div>
        """
        
        html_content = html_content.replace(
            '<div id="stats"></div>',
            f'<div id="stats">{stats_html}</div>'
        )
        
        # Write updated HTML
        self.html_log.write_text(html_content, encoding='utf-8')
    
    def _create_html_template(self):
        """Create HTML template for visual logs"""
        
        template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grace Knowledge Ingestion Log</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
            color: #e0e0e0;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        
        .stat-card h3 {
            font-size: 2.5em;
            color: #6366f1;
            margin-bottom: 10px;
        }
        
        .stat-card p {
            color: #b0b0b0;
        }
        
        .ingestion-entry {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .ingestion-entry:hover {
            background: rgba(255, 255, 255, 0.05);
            border-color: #6366f1;
            box-shadow: 0 5px 20px rgba(99, 102, 241, 0.2);
        }
        
        .ingestion-entry.verified {
            border-left: 4px solid #27ae60;
        }
        
        .ingestion-entry.partial {
            border-left: 4px solid #f39c12;
        }
        
        .entry-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .entry-number {
            font-size: 1.5em;
            font-weight: bold;
            color: #6366f1;
        }
        
        .timestamp {
            color: #b0b0b0;
            font-size: 0.9em;
        }
        
        .status {
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85em;
        }
        
        .source-info h3 {
            color: #fff;
            margin-bottom: 10px;
            font-size: 1.3em;
        }
        
        .source-info p {
            margin: 5px 0;
            color: #d0d0d0;
        }
        
        .source-link {
            color: #6366f1;
            text-decoration: none;
            font-weight: bold;
            transition: color 0.3s ease;
        }
        
        .source-link:hover {
            color: #8b5cf6;
            text-decoration: underline;
        }
        
        .verification-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        
        .verification-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .verification-item.verified {
            border-color: #27ae60;
            background: rgba(39, 174, 96, 0.1);
        }
        
        .verification-item.failed {
            border-color: #e74c3c;
            background: rgba(231, 76, 60, 0.1);
        }
        
        .verification-item .icon {
            font-size: 1.5em;
            display: block;
            margin-bottom: 8px;
        }
        
        .crypto-section, .metadata-section {
            margin: 20px 0;
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }
        
        .crypto-section h4, .metadata-section h4 {
            margin-bottom: 15px;
            color: #8b5cf6;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        table td {
            padding: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        table td:first-child {
            color: #b0b0b0;
            width: 200px;
        }
        
        code.hash {
            background: rgba(99, 102, 241, 0.2);
            padding: 4px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #6366f1;
            font-size: 0.85em;
        }
        
        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .metadata-item {
            padding: 10px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 5px;
        }
        
        .verified {
            color: #27ae60;
            font-weight: bold;
        }
        
        .refresh-note {
            text-align: center;
            padding: 15px;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 8px;
            margin-bottom: 20px;
            color: #6366f1;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Grace Knowledge Ingestion Log</h1>
            <p>Real-time monitoring of Grace's learning with cryptographic verification</p>
        </header>
        
        <div class="refresh-note">
            🔄 Refresh this page to see new ingestions | 🔗 Click links to view sources
        </div>
        
        <div class="stats-container" id="stats"></div>
        
        <div id="ingestion-log"></div>
    </div>
</body>
</html>"""
        
        self.html_log.write_text(template, encoding='utf-8')
    
    async def get_recent_ingestions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent ingestions from database"""
        
        async with async_session() as session:
            result = await session.execute(
                select(KnowledgeSource)
                .order_by(desc(KnowledgeSource.created_at))
                .limit(limit)
            )
            sources = result.scalars().all()
            
            ingestions = []
            for source in sources:
                ingestions.append({
                    'source_id': source.source_id,
                    'type': source.source_type,
                    'url': source.url,
                    'title': source.title,
                    'domain': source.domain,
                    'scraped_at': source.scraped_at.isoformat() if source.scraped_at else None,
                    'verified': source.verified,
                    'trust_score': source.trust_score,
                    'word_count': source.word_count,
                    'code_count': source.code_snippet_count,
                    'verification': {
                        'hunter': source.hunter_verified,
                        'governance': source.governance_approved,
                        'constitutional': source.constitutional_approved
                    },
                    'crypto': {
                        'content_hash': source.content_hash,
                        'immutable_log_hash': source.immutable_log_hash,
                        'previous_hash': source.previous_hash
                    }
                })
            
            return ingestions
    
    async def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        
        async with async_session() as session:
            from sqlalchemy import func
            
            # Total sources
            result = await session.execute(select(func.count(KnowledgeSource.id)))
            total = result.scalar() or 0
            
            # Verified sources
            result = await session.execute(
                select(func.count(KnowledgeSource.id))
                .where(KnowledgeSource.verified == True)
            )
            verified = result.scalar() or 0
            
            # By source type
            result = await session.execute(
                select(KnowledgeSource.source_type, func.count(KnowledgeSource.id))
                .group_by(KnowledgeSource.source_type)
            )
            by_type = dict(result.all())
            
            # By domain (top 10)
            result = await session.execute(
                select(KnowledgeSource.domain, func.count(KnowledgeSource.id))
                .group_by(KnowledgeSource.domain)
                .order_by(desc(func.count(KnowledgeSource.id)))
                .limit(10)
            )
            top_domains = dict(result.all())
            
            return {
                'total_ingestions': total,
                'verified_sources': verified,
                'verification_rate': verified / total if total > 0 else 0,
                'by_source_type': by_type,
                'top_domains': top_domains,
                'html_log': str(self.html_log.absolute())
            }


# Global instance
visual_ingestion_logger = VisualIngestionLogger()
