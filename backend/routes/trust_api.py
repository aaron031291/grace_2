"""
Trust & Quality API Routes
Endpoints for trust scoring and contradiction detection
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter(prefix="/api/memory/tables", tags=["trust-quality"])


@router.get("/trust/report")
async def get_trust_report():
    """Get comprehensive trust report across all tables"""
    try:
        from backend.memory_tables.trust_scoring import trust_scoring_engine
        
        report = await trust_scoring_engine.get_trust_report()
        return report
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trust/update/{table_name}")
async def update_trust_scores(table_name: str, limit: int = 1000):
    """Update trust scores for a specific table"""
    try:
        from backend.memory_tables.trust_scoring import trust_scoring_engine
        
        updated_count = await trust_scoring_engine.update_all_trust_scores(table_name, limit)
        
        return {
            'success': True,
            'table': table_name,
            'updated_count': updated_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trust/update-all")
async def update_all_trust_scores(limit: int = 1000):
    """Update trust scores for all tables"""
    try:
        from backend.memory_tables.trust_scoring import trust_scoring_engine
        from backend.memory_tables.registry import table_registry
        
        total_updated = 0
        results = {}
        
        for table_name in table_registry.list_tables():
            try:
                count = await trust_scoring_engine.update_all_trust_scores(table_name, limit)
                results[table_name] = count
                total_updated += count
            except Exception as e:
                results[table_name] = f"Error: {str(e)}"
        
        return {
            'success': True,
            'total_updated': total_updated,
            'by_table': results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contradictions/summary")
async def get_contradiction_summary():
    """Get summary of contradictions across all tables"""
    try:
        from backend.memory_tables.contradiction_detector import contradiction_detector
        
        summary = await contradiction_detector.get_contradiction_summary()
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contradictions/scan")
async def scan_contradictions(table_name: Optional[str] = None):
    """Scan for contradictions in all tables or a specific table"""
    try:
        from backend.memory_tables.contradiction_detector import contradiction_detector
        
        if table_name:
            contradictions = await contradiction_detector.detect_contradictions(table_name)
            return {
                'success': True,
                'table': table_name,
                'contradictions': contradictions,
                'total_contradictions': len(contradictions)
            }
        else:
            all_contradictions = await contradiction_detector.scan_all_tables()
            total = sum(len(c) for c in all_contradictions.values())
            
            return {
                'success': True,
                'all_tables': all_contradictions,
                'total_contradictions': total
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contradictions/{table_name}")
async def get_table_contradictions(table_name: str):
    """Get contradictions for a specific table"""
    try:
        from backend.memory_tables.contradiction_detector import contradiction_detector
        
        contradictions = await contradiction_detector.detect_contradictions(table_name)
        
        return {
            'success': True,
            'table': table_name,
            'contradictions': contradictions,
            'count': len(contradictions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
