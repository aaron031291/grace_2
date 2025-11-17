"""
Business Data Warehouse

Normalized schema for all business intelligence:
- Customer segments & profiles
- Product performance
- Channel analytics
- Financial metrics
- Business opportunities
"""

import sqlite3
from typing import Dict, Any, List
import json

DB_PATH = "databases/memory_tables.db"


class BusinessWarehouse:
    """Business intelligence data warehouse"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Create warehouse tables"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Customer Segments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_customer_segments (
                segment_id TEXT PRIMARY KEY,
                segment_name TEXT NOT NULL,
                customer_count INTEGER DEFAULT 0,
                avg_ltv REAL DEFAULT 0.0,
                avg_cac REAL DEFAULT 0.0,
                ltv_cac_ratio REAL DEFAULT 0.0,
                churn_rate REAL DEFAULT 0.0,
                monthly_revenue REAL DEFAULT 0.0,
                opportunity_score REAL DEFAULT 0.0,
                recommended_actions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Product Performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_product_performance (
                product_id TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT,
                revenue_30d REAL DEFAULT 0.0,
                revenue_90d REAL DEFAULT 0.0,
                units_sold_30d INTEGER DEFAULT 0,
                margin_percent REAL DEFAULT 0.0,
                velocity_score REAL DEFAULT 0.0,
                growth_rate REAL DEFAULT 0.0,
                opportunity_score REAL DEFAULT 0.0,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Channel Performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_channel_performance (
                channel_id TEXT PRIMARY KEY,
                channel_name TEXT NOT NULL,
                channel_type TEXT,
                traffic_volume_30d INTEGER DEFAULT 0,
                conversion_rate REAL DEFAULT 0.0,
                cpa REAL DEFAULT 0.0,
                roas REAL DEFAULT 0.0,
                ltv_cac_ratio REAL DEFAULT 0.0,
                trend TEXT,
                opportunity_score REAL DEFAULT 0.0,
                recommended_playbook TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Financial Metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_financial_metrics (
                metric_id TEXT PRIMARY KEY,
                metric_date DATE NOT NULL,
                mrr REAL DEFAULT 0.0,
                arr REAL DEFAULT 0.0,
                churn_rate REAL DEFAULT 0.0,
                arpu REAL DEFAULT 0.0,
                cac REAL DEFAULT 0.0,
                ltv REAL DEFAULT 0.0,
                runway_months INTEGER DEFAULT 0,
                burn_rate REAL DEFAULT 0.0,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Business Opportunities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_business_opportunities (
                opportunity_id TEXT PRIMARY KEY,
                niche_name TEXT NOT NULL,
                category TEXT,
                opportunity_score REAL NOT NULL,
                demand_score REAL DEFAULT 0.0,
                competition_score REAL DEFAULT 0.0,
                alignment_score REAL DEFAULT 0.0,
                revenue_potential REAL DEFAULT 0.0,
                recommended_actions TEXT,
                book_frameworks TEXT,
                evidence TEXT,
                status TEXT DEFAULT 'identified',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Business Events (staging table for raw data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_business_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                event_source TEXT NOT NULL,
                event_data TEXT NOT NULL,
                processed BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_customer_segment(self, segment: Dict[str, Any]):
        """Insert or update customer segment"""
        
        conn = sqlite3.connect(self.db_path)
        
        conn.execute("""
            INSERT OR REPLACE INTO memory_customer_segments
            (segment_id, segment_name, customer_count, avg_ltv, avg_cac, 
             ltv_cac_ratio, churn_rate, monthly_revenue, opportunity_score,
             recommended_actions, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            segment['segment_id'],
            segment['segment_name'],
            segment.get('customer_count', 0),
            segment.get('avg_ltv', 0.0),
            segment.get('avg_cac', 0.0),
            segment.get('ltv_cac_ratio', 0.0),
            segment.get('churn_rate', 0.0),
            segment.get('monthly_revenue', 0.0),
            segment.get('opportunity_score', 0.0),
            json.dumps(segment.get('recommended_actions', []))
        ))
        
        conn.commit()
        conn.close()
    
    def insert_opportunity(self, opportunity: Dict[str, Any]):
        """Insert business opportunity"""
        
        conn = sqlite3.connect(self.db_path)
        
        conn.execute("""
            INSERT OR REPLACE INTO memory_business_opportunities
            (opportunity_id, niche_name, category, opportunity_score,
             demand_score, competition_score, alignment_score,
             revenue_potential, recommended_actions, book_frameworks,
             evidence, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            opportunity['opportunity_id'],
            opportunity['niche_name'],
            opportunity.get('category', ''),
            opportunity['opportunity_score'],
            opportunity.get('demand_score', 0.0),
            opportunity.get('competition_score', 0.0),
            opportunity.get('alignment_score', 0.0),
            opportunity.get('revenue_potential', 0.0),
            json.dumps(opportunity.get('recommended_actions', [])),
            json.dumps(opportunity.get('book_frameworks', [])),
            json.dumps(opportunity.get('evidence', {})),
            opportunity.get('status', 'identified')
        ))
        
        conn.commit()
        conn.close()
    
    def get_top_opportunities(self, limit: int = 10) -> List[Dict]:
        """Get top business opportunities"""
        
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute("""
            SELECT opportunity_id, niche_name, category, opportunity_score,
                   demand_score, competition_score, revenue_potential,
                   recommended_actions, book_frameworks, status
            FROM memory_business_opportunities
            WHERE status != 'rejected'
            ORDER BY opportunity_score DESC
            LIMIT ?
        """, (limit,))
        
        opportunities = []
        for row in cursor.fetchall():
            opportunities.append({
                'opportunity_id': row[0],
                'niche_name': row[1],
                'category': row[2],
                'opportunity_score': row[3],
                'demand_score': row[4],
                'competition_score': row[5],
                'revenue_potential': row[6],
                'recommended_actions': json.loads(row[7]) if row[7] else [],
                'book_frameworks': json.loads(row[8]) if row[8] else [],
                'status': row[9]
            })
        
        conn.close()
        return opportunities


# Singleton
_warehouse = None

def get_warehouse() -> BusinessWarehouse:
    global _warehouse
    if _warehouse is None:
        _warehouse = BusinessWarehouse()
    return _warehouse
