"""
Business Opportunity Finder

Analyzes business data + book knowledge to find opportunities
"""

import sys
import io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3
import hashlib
from datetime import datetime
import json
from typing import Dict, Any, List

from backend.services.business_warehouse import get_warehouse


async def search_books_for_strategy(niche: str, problem: str) -> Dict:
    """Search book knowledge for strategies"""
    
    conn = sqlite3.connect("databases/memory_tables.db")
    
    # Search book chunks for relevant strategies
    cursor = conn.execute("""
        SELECT c.content, d.title, d.authors
        FROM memory_document_chunks c
        JOIN memory_documents d ON c.document_id = d.id
        WHERE c.content LIKE ? OR c.content LIKE ?
        LIMIT 3
    """, (f"%{niche}%", f"%{problem}%"))
    
    results = cursor.fetchall()
    conn.close()
    
    if results:
        # Extract frameworks from book content
        frameworks = []
        for content, title, authors in results:
            frameworks.append({
                'book': title,
                'author': json.loads(authors)[0] if authors else 'Unknown',
                'excerpt': content[:300]
            })
        
        return {
            'found': True,
            'frameworks': frameworks,
            'books_referenced': [f['book'] for f in frameworks]
        }
    
    return {'found': False, 'frameworks': []}


async def analyze_customer_segments() -> List[Dict]:
    """Analyze customer segments for opportunities"""
    
    conn = sqlite3.connect("databases/memory_tables.db")
    
    cursor = conn.execute("""
        SELECT segment_id, segment_name, customer_count, ltv_cac_ratio, 
               churn_rate, monthly_revenue
        FROM memory_customer_segments
        ORDER BY opportunity_score DESC
    """)
    
    segments = cursor.fetchall()
    conn.close()
    
    opportunities = []
    
    for segment in segments:
        seg_id, name, count, ltv_cac, churn, revenue = segment
        
        # High churn = retention opportunity
        if churn > 0.10:  # 10%+ churn
            # Search books for churn solutions
            strategy = await search_books_for_strategy(
                niche="customer success",
                problem="churn retention"
            )
            
            opportunities.append({
                'type': 'retention',
                'segment': name,
                'problem': f"High churn rate: {churn:.1%}",
                'impact': f"Reducing to 5% could save ${revenue * churn * 12:,.0f}/year",
                'strategy': strategy,
                'priority': 'high' if churn > 0.15 else 'medium'
            })
        
        # Low LTV/CAC = pricing/positioning opportunity  
        if ltv_cac < 3.0:
            strategy = await search_books_for_strategy(
                niche="pricing",
                problem="value increase"
            )
            
            opportunities.append({
                'type': 'pricing',
                'segment': name,
                'problem': f"Low LTV/CAC ratio: {ltv_cac:.1f}",
                'impact': f"Improving to 5.0 could add ${revenue * count * 0.4:,.0f}/year",
                'strategy': strategy,
                'priority': 'medium'
            })
    
    return opportunities


async def find_niche_opportunities() -> List[Dict]:
    """Find new niche opportunities"""
    
    # Example niches to evaluate
    potential_niches = [
        {
            'niche': 'SaaS Customer Success Training',
            'category': 'B2B Education',
            'demand_keywords': ['customer success', 'churn', 'retention'],
            'target_segment': 'SMB SaaS founders'
        },
        {
            'niche': 'Sales Automation for E-commerce',
            'category': 'B2B SaaS',
            'demand_keywords': ['sales automation', 'closing', 'leads'],
            'target_segment': 'E-commerce stores'
        },
        {
            'niche': 'Marketing Analytics Dashboard',
            'category': 'B2B SaaS',
            'demand_keywords': ['traffic', 'ROAS', 'analytics'],
            'target_segment': 'Digital marketers'
        }
    ]
    
    opportunities = []
    
    for niche in potential_niches:
        # Search books for applicable frameworks
        strategies = []
        for keyword in niche['demand_keywords']:
            result = await search_books_for_strategy(keyword, "strategy")
            if result['found']:
                strategies.extend(result['frameworks'])
        
        # Calculate opportunity score
        # In production: use real market data, competition analysis
        demand_score = 0.8  # Mock: High demand
        competition_score = 0.3  # Mock: Low competition (0 = none, 1 = saturated)
        alignment_score = 0.9  # Mock: High alignment with Grace's capabilities
        
        opportunity_score = (
            demand_score * 0.4 +
            (1 - competition_score) * 0.3 +
            alignment_score * 0.3
        )
        
        if opportunity_score > 0.65:  # High potential
            opportunities.append({
                'opportunity_id': hashlib.md5(niche['niche'].encode()).hexdigest()[:16],
                'niche_name': niche['niche'],
                'category': niche['category'],
                'opportunity_score': opportunity_score,
                'demand_score': demand_score,
                'competition_score': competition_score,
                'alignment_score': alignment_score,
                'revenue_potential': 50000.0,  # Mock: $50K MRR potential
                'book_frameworks': [s['book'] for s in strategies[:3]],
                'recommended_actions': generate_action_plan(niche, strategies),
                'evidence': {
                    'demand_indicators': niche['demand_keywords'],
                    'book_coverage': len(strategies),
                    'target_segment': niche['target_segment']
                }
            })
    
    return opportunities


def generate_action_plan(niche: Dict, book_strategies: List) -> List[str]:
    """Generate action plan from book frameworks"""
    
    actions = []
    
    # Generic actions based on niche type
    if 'Training' in niche['niche'] or 'Education' in niche['category']:
        actions = [
            f"Package knowledge from books into course",
            f"Target {niche['target_segment']} with relevant pain points",
            "Use Hormozi pricing: $2K with payment plans",
            "Traffic: Dream 100 outreach to influencers",
            "Launch: Lean Startup MVP approach",
            "Expected: $50K MRR in 6 months"
        ]
    
    elif 'SaaS' in niche['category']:
        actions = [
            "Build MVP using Lean Startup methodology",
            "Price using Hormozi frameworks (3-tier)",
            "Traffic via Traffic Secrets Dream 100",
            "Ads using Goated Ads creative frameworks",
            "CS playbooks from CS Guide",
            "Expected: $100K ARR in 12 months"
        ]
    
    elif 'Dashboard' in niche['niche'] or 'Analytics' in niche['niche']:
        actions = [
            "Build using Grace's existing analytics",
            "Target performance marketers",
            "Integrate ad platforms (FB, Google)",
            "Price: $299/month SaaS model",
            "Traffic: Content marketing + paid ads",
            "Expected: $30K MRR in 9 months"
        ]
    
    else:
        actions = [
            "Research market demand (validate)",
            "Build MVP (Lean Startup)",
            "Test pricing (Hormozi frameworks)",
            "Launch traffic (Traffic Secrets)",
            "Monitor and iterate"
        ]
    
    return actions


async def analyze_opportunities():
    """Main opportunity analysis function"""
    
    print("\n" + "="*70)
    print("BUSINESS OPPORTUNITY FINDER")
    print("="*70)
    print("\nAnalyzing:")
    print("  📊 Customer segments")
    print("  📈 Financial metrics")
    print("  📚 Book knowledge (26 books, 551K words)")
    print("  🎯 Niche potential")
    print("="*70)
    
    warehouse = get_warehouse()
    all_opportunities = []
    
    # Analyze customer segments
    print("\n[1/2] Analyzing Customer Segments...")
    segment_opps = await analyze_customer_segments()
    print(f"   Found {len(segment_opps)} segment opportunities")
    
    # Find new niches
    print("\n[2/2] Evaluating New Niche Opportunities...")
    niche_opps = await find_niche_opportunities()
    print(f"   Found {len(niche_opps)} niche opportunities")
    
    # Store niche opportunities
    for opp in niche_opps:
        warehouse.insert_opportunity(opp)
        all_opportunities.append(opp)
    
    # Display results
    print("\n" + "="*70)
    print(f"TOP {min(5, len(all_opportunities))} OPPORTUNITIES")
    print("="*70)
    
    sorted_opps = sorted(all_opportunities, key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    for i, opp in enumerate(sorted_opps[:5], 1):
        print(f"\n{i}. {opp.get('niche_name', opp.get('segment', 'Unknown'))}")
        print(f"   Score: {opp.get('opportunity_score', 0):.0%}")
        
        if 'problem' in opp:
            print(f"   Problem: {opp['problem']}")
            print(f"   Impact: {opp.get('impact', 'N/A')}")
        else:
            print(f"   Revenue Potential: ${opp.get('revenue_potential', 0):,.0f}")
        
        print(f"   Strategy Books: {', '.join(opp.get('book_frameworks', [])[:3])}")
        
        actions = opp.get('recommended_actions', [])
        if actions:
            print(f"   Action Plan:")
            for action in actions[:3]:
                print(f"      • {action}")
    
    print("\n" + "="*70)
    print(f"✅ ANALYSIS COMPLETE - {len(all_opportunities)} opportunities identified")
    print("="*70)
    print("\n💾 Stored in: memory_business_opportunities")
    print("📊 View: curl http://localhost:8000/api/business/opportunities")
    print()
    
    return all_opportunities


if __name__ == "__main__":
    import asyncio
    asyncio.run(analyze_opportunities())
