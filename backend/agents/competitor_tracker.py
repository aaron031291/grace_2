"""
Competitor Campaign Tracker
Monitors competitor marketing campaigns, extracts winning patterns
"""

import logging
from typing import Dict, Any
from datetime import datetime
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class CompetitorTracker:
    """
    Tracks competitor marketing campaigns across platforms:
    - Facebook Ad Library (Meta ads)
    - TikTok Creative Center
    - Google Ads Transparency
    - Competitor websites
    
    Learns what works and builds competitive intelligence
    """
    
    def __init__(self):
        self.curriculum = None
        self.tracked_competitors = []
        self.campaigns_tracked = 0
        self.ads_downloaded = 0
        self.patterns_identified = 0
        self._initialized = False
        
        # Storage
        self.data_dir = Path(__file__).parent.parent.parent / "grace_training" / "marketing"
        self.competitor_ads_dir = self.data_dir / "competitor_ads"
        self.tiktok_campaigns_dir = self.data_dir / "tiktok_campaigns"
        self.landing_pages_dir = self.data_dir / "landing_pages"
        self.patterns_dir = self.data_dir / "winning_patterns"
        
        # Create directories
        for directory in [
            self.competitor_ads_dir,
            self.tiktok_campaigns_dir,
            self.landing_pages_dir,
            self.patterns_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Load competitor tracking curriculum"""
        if self._initialized:
            return
        
        try:
            curriculum_path = Path(__file__).parent.parent.parent / "config" / "competitor_tracking_curriculum.yaml"
            if curriculum_path.exists():
                with open(curriculum_path, 'r', encoding='utf-8') as f:
                    docs = list(yaml.safe_load_all(f))
                    self.curriculum = docs[0] if docs else {}
                logger.info("[COMPETITOR-TRACKER] Loaded competitor tracking curriculum")
            else:
                logger.warning(f"[COMPETITOR-TRACKER] Curriculum not found: {curriculum_path}")
        except Exception as e:
            logger.error(f"[COMPETITOR-TRACKER] Failed to load curriculum: {e}")
        
        self._initialized = True
        logger.info("[COMPETITOR-TRACKER] Competitor tracking system ready")
    
    async def track_facebook_ads(
        self,
        competitor_name: str
    ) -> Dict[str, Any]:
        """
        Track competitor ads from Facebook Ad Library
        
        Args:
            competitor_name: Competitor brand/company name
        
        Returns:
            All active ads with metadata
        """
        from backend.services.google_search_service import google_search_service
        
        logger.info(f"[COMPETITOR-TRACKER] 📊 Tracking Facebook ads for: {competitor_name}")
        
        # Search Facebook Ad Library
        search_query = f'site:facebook.com/ads/library "{competitor_name}"'
        
        try:
            results = await google_search_service.search(
                query=search_query,
                num_results=10,
                min_trust_score=0.9
            )
            
            ads_found = []
            
            for result in results:
                ad_data = {
                    'competitor': competitor_name,
                    'platform': 'meta',
                    'url': result.get('url', ''),
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'discovered_at': datetime.utcnow().isoformat(),
                    'trust_score': result.get('trust_score', 0.9)
                }
                ads_found.append(ad_data)
            
            # Save findings
            if ads_found:
                self.campaigns_tracked += 1
                self.ads_downloaded += len(ads_found)
                
                # Save to file
                import json
                output_file = self.competitor_ads_dir / f"{competitor_name.replace(' ', '_')}_meta_ads.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(ads_found, f, indent=2)
                
                logger.info(f"[COMPETITOR-TRACKER] ✅ Found {len(ads_found)} ads, saved to {output_file.name}")
            
            return {
                'competitor': competitor_name,
                'platform': 'meta',
                'ads_found': len(ads_found),
                'ads': ads_found,
                'saved_to': str(output_file) if ads_found else None
            }
        
        except Exception as e:
            logger.error(f"[COMPETITOR-TRACKER] Failed to track Facebook ads: {e}")
            return {
                'competitor': competitor_name,
                'error': str(e),
                'ads_found': 0
            }
    
    async def track_tiktok_campaigns(
        self,
        industry: str = "general"
    ) -> Dict[str, Any]:
        """
        Track trending TikTok campaigns and products
        """
        from backend.services.google_search_service import google_search_service
        
        logger.info(f"[COMPETITOR-TRACKER] 📱 Tracking TikTok campaigns for: {industry}")
        
        search_queries = [
            f"site:tiktok.com trending {industry} products",
            f"TikTok Shop {industry} best sellers",
            f"viral TikTok {industry} campaigns"
        ]
        
        all_campaigns = []
        
        for query in search_queries[:2]:
            try:
                results = await google_search_service.search(
                    query=query,
                    num_results=5
                )
                
                for result in results:
                    campaign = {
                        'platform': 'tiktok',
                        'industry': industry,
                        'url': result.get('url', ''),
                        'title': result.get('title', ''),
                        'description': result.get('snippet', ''),
                        'discovered_at': datetime.utcnow().isoformat()
                    }
                    all_campaigns.append(campaign)
            
            except Exception as e:
                logger.warning(f"[COMPETITOR-TRACKER] TikTok query failed: {e}")
        
        # Save findings
        if all_campaigns:
            import json
            output_file = self.tiktok_campaigns_dir / f"{industry}_tiktok_campaigns.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_campaigns, f, indent=2)
            
            logger.info(f"[COMPETITOR-TRACKER] ✅ Found {len(all_campaigns)} TikTok campaigns")
        
        return {
            'industry': industry,
            'campaigns_found': len(all_campaigns),
            'campaigns': all_campaigns
        }
    
    async def analyze_campaign_patterns(
        self,
        platform: str = "all"
    ) -> Dict[str, Any]:
        """
        Analyze tracked campaigns to identify winning patterns
        
        Returns patterns that work across campaigns
        """
        logger.info(f"[COMPETITOR-TRACKER] 🔍 Analyzing campaign patterns for: {platform}")
        
        patterns = {
            'platform': platform,
            'analysis_date': datetime.utcnow().isoformat(),
            'patterns_found': [],
            'recommendations': []
        }
        
        # Load all saved campaign data
        import json
        
        campaign_files = list(self.competitor_ads_dir.glob('*.json'))
        campaign_files.extend(self.tiktok_campaigns_dir.glob('*.json'))
        
        all_campaigns = []
        for file in campaign_files[:50]:  # Limit to prevent overload
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_campaigns.extend(data)
                    else:
                        all_campaigns.append(data)
            except Exception as e:
                logger.warning(f"[COMPETITOR-TRACKER] Failed to load {file}: {e}")
        
        # Pattern analysis (simplified - can be enhanced with NLP)
        if all_campaigns:
            # Extract common elements
            headlines = [c.get('title', '') for c in all_campaigns if c.get('title')]
            snippets = [c.get('snippet', '') for c in all_campaigns if c.get('snippet')]
            
            # Identify common words in successful campaigns
            from collections import Counter
            import re
            
            all_words = []
            for text in headlines + snippets:
                words = re.findall(r'\b\w+\b', text.lower())
                all_words.extend([w for w in words if len(w) > 3])
            
            common_words = Counter(all_words).most_common(20)
            
            patterns['patterns_found'].append({
                'pattern_type': 'common_words',
                'words': [{'word': w, 'frequency': f} for w, f in common_words]
            })
            
            # Recommendations based on patterns
            top_words = [w for w, f in common_words[:10]]
            patterns['recommendations'].append(
                f"Consider using these high-frequency words in campaigns: {', '.join(top_words)}"
            )
            
            self.patterns_identified += 1
        
        logger.info(f"[COMPETITOR-TRACKER] ✅ Identified {len(patterns['patterns_found'])} patterns")
        
        return patterns
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get competitor tracking metrics"""
        return {
            'competitors_tracked': len(self.tracked_competitors),
            'campaigns_tracked': self.campaigns_tracked,
            'ads_downloaded': self.ads_downloaded,
            'patterns_identified': self.patterns_identified,
            'initialized': self._initialized
        }


# Global instance
competitor_tracker = CompetitorTracker()
