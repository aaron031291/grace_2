"""
Business Intelligence API

Provides access to:
- Business opportunities
- Customer segment analysis
- Channel performance
- Financial metrics
- Book-based recommendations
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import sqlite3

router = APIRouter(prefix="/business", tags=["Business Intelligence"])

DB_PATH = "databases/memory_tables.db"


@router.get("/opportunities")
async def get_opportunities(
    min_score: float = 0.0,
    category: str = None,
    limit: int = 10
) -> Dict[str, Any]:
    """Get business opportunities ranked by score"""
    
    from backend.services.business_warehouse import get_warehouse
    
    warehouse = get_warehouse()
    opportunities = warehouse.get_top_opportunities(limit=limit)
    
    # Filter by score and category
    if min_score > 0:
        opportunities = [o for o in opportunities if o['opportunity_score'] >= min_score]
    
    if category:
        opportunities = [o for o in opportunities if o.get('category') == category]
    
    return {
        'opportunities': opportunities,
        'count': len(opportunities),
        'data_sources': ['stripe', 'customer_segments', 'book_knowledge'],
        'books_analyzed': 26
    }


@router.get("/segments")
async def get_customer_segments() -> Dict[str, Any]:
    """Get customer segment analysis"""
    
    conn = sqlite3.connect(DB_PATH)
    
    cursor = conn.execute("""
        SELECT segment_id, segment_name, customer_count, avg_ltv, avg_cac,
               ltv_cac_ratio, churn_rate, monthly_revenue, opportunity_score
        FROM memory_customer_segments
        ORDER BY opportunity_score DESC
    """)
    
    segments = []
    for row in cursor.fetchall():
        segments.append({
            'segment_id': row[0],
            'segment_name': row[1],
            'customer_count': row[2],
            'avg_ltv': row[3],
            'avg_cac': row[4],
            'ltv_cac_ratio': row[5],
            'churn_rate': row[6],
            'monthly_revenue': row[7],
            'opportunity_score': row[8]
        })
    
    conn.close()
    
    return {
        'segments': segments,
        'count': len(segments),
        'total_customers': sum(s['customer_count'] for s in segments),
        'total_mrr': sum(s['monthly_revenue'] for s in segments)
    }


@router.get("/metrics")
async def get_financial_metrics() -> Dict[str, Any]:
    """Get latest financial metrics"""
    
    conn = sqlite3.connect(DB_PATH)
    
    cursor = conn.execute("""
        SELECT mrr, arr, churn_rate, arpu, cac, ltv, runway_months, burn_rate
        FROM memory_financial_metrics
        ORDER BY created_at DESC
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {
            'error': 'No financial metrics found',
            'suggestion': 'Run: python scripts/connectors/stripe_connector.py'
        }
    
    return {
        'mrr': row[0],
        'arr': row[1],
        'churn_rate': row[2],
        'arpu': row[3],
        'cac': row[4],
        'ltv': row[5],
        'runway_months': row[6],
        'burn_rate': row[7],
        'ltv_cac_ratio': row[5] / row[4] if row[4] > 0 else 0
    }


@router.post("/analyze")
async def analyze_business() -> Dict[str, Any]:
    """Run complete business analysis"""
    
    # Run opportunity finder
    from scripts.analyze_business_opportunities import analyze_opportunities
    
    opportunities = await analyze_opportunities()
    
    return {
        'status': 'completed',
        'opportunities_found': len(opportunities),
        'top_opportunities': opportunities[:5],
        'message': 'Analysis complete. Check /business/opportunities for full list.'
    }


@router.get("/recommendations/{segment_id}")
async def get_segment_recommendations(segment_id: str) -> Dict[str, Any]:
    """Get book-based recommendations for a customer segment"""
    
    conn = sqlite3.connect(DB_PATH)
    
    # Get segment data
    cursor = conn.execute("""
        SELECT segment_name, churn_rate, ltv_cac_ratio, monthly_revenue
        FROM memory_customer_segments
        WHERE segment_id = ?
    """, (segment_id,))
    
    segment = cursor.fetchone()
    conn.close()
    
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    name, churn, ltv_cac, revenue = segment
    
    # Generate recommendations from books
    recommendations = []
    
    if churn > 0.10:
        recommendations.append({
            'issue': f'High churn: {churn:.1%}',
            'book': 'Customer Success for SaaS Companies',
            'recommendation': 'Implement health scoring and proactive intervention',
            'expected_impact': f'Reduce churn to 5%, save ${revenue * churn * 12:,.0f}/year'
        })
    
    if ltv_cac < 3.0:
        recommendations.append({
            'issue': f'Low LTV/CAC: {ltv_cac:.1f}',
            'book': '$100M Fast Cash Playbook',
            'recommendation': 'Implement payment plans to increase AOV',
            'expected_impact': 'Increase LTV by 40-60%'
        })
    
    return {
        'segment': name,
        'segment_id': segment_id,
        'recommendations': recommendations,
        'books_analyzed': 26
    }


@router.get("/daily-brief")
async def get_daily_brief() -> Dict[str, Any]:
    """Get daily business intelligence brief"""
    
    try:
        # Get top opportunities
        from backend.services.business_warehouse import get_warehouse
        warehouse = get_warehouse()
        opportunities = warehouse.get_top_opportunities(limit=5)
        
        # Get metrics
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("""
            SELECT mrr, churn_rate FROM memory_financial_metrics
            ORDER BY created_at DESC LIMIT 1
        """)
        
        metrics = cursor.fetchone()
        conn.close()
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'summary': f"You have {len(opportunities)} high-potential opportunities",
            'metrics': {
                'mrr': metrics[0] if metrics else 0,
                'churn_rate': metrics[1] if metrics else 0
            },
            'top_opportunities': opportunities[:3],
            'recommended_focus': opportunities[0]['niche_name'] if opportunities else 'No opportunities identified',
            'books_powering_analysis': 26,
            'total_words_analyzed': 551469
        }
    except Exception as e:
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'error': str(e),
            'opportunities': [],
            'books_analyzed': 26
        }
