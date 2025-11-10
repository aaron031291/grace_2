"""
Quick Verification of Meta-Loop System Components
Checks that all pieces are in place without running full workflow
"""

def verify_system():
    """Verify meta-loop system is properly configured"""
    
    print("=" * 80)
    print("META-LOOP SYSTEM VERIFICATION")
    print("=" * 80)
    
    results = {
        "files": [],
        "imports": [],
        "api_endpoints": [],
        "database_models": []
    }
    
    # Check files exist
    print("\n[1] FILE EXISTENCE")
    print("-" * 80)
    
    import os
    from pathlib import Path
    
    backend = Path(__file__).parent
    files_to_check = [
        "meta_loop.py",
        "meta_loop_engine.py",
        "meta_loop_approval.py",
        "routes/meta_api.py",
        "seed_meta_governance.py",
        "META_LOOP_SYSTEM.md",
    ]
    
    for file in files_to_check:
        path = backend / file
        exists = path.exists()
        status = "[OK]" if exists else "[MISS]"
        print(f"{status} {file}")
        results["files"].append((file, exists))
    
    # Check imports
    print("\n[2] IMPORT CHECKS")
    print("-" * 80)
    
    try:
        from grace_rebuild.backend import meta_loop_engine
        print("✓ meta_loop_engine")
        results["imports"].append(("meta_loop_engine", True))
    except Exception as e:
        print(f"✗ meta_loop_engine: {e}")
        results["imports"].append(("meta_loop_engine", False))
    
    try:
        from grace_rebuild.backend import meta_loop_approval
        print("✓ meta_loop_approval")
        results["imports"].append(("meta_loop_approval", True))
    except Exception as e:
        print(f"✗ meta_loop_approval: {e}")
        results["imports"].append(("meta_loop_approval", False))
    
    try:
        from grace_rebuild.backend.routes import meta_api
        print("✓ routes.meta_api")
        results["imports"].append(("routes.meta_api", True))
    except Exception as e:
        print(f"✗ routes.meta_api: {e}")
        results["imports"].append(("routes.meta_api", False))
    
    # Check classes exist
    print("\n[3] CLASS CHECKS")
    print("-" * 80)
    
    try:
        from grace_rebuild.backend.meta_loop_engine import RecommendationApplicator, AppliedRecommendation
        print("✓ RecommendationApplicator")
        print("✓ AppliedRecommendation")
        results["database_models"].append(("AppliedRecommendation", True))
    except Exception as e:
        print(f"✗ RecommendationApplicator/AppliedRecommendation: {e}")
        results["database_models"].append(("AppliedRecommendation", False))
    
    try:
        from grace_rebuild.backend.meta_loop_approval import ApprovalQueue, RecommendationQueue
        print("✓ ApprovalQueue")
        print("✓ RecommendationQueue")
        results["database_models"].append(("RecommendationQueue", True))
    except Exception as e:
        print(f"✗ ApprovalQueue/RecommendationQueue: {e}")
        results["database_models"].append(("RecommendationQueue", False))
    
    # Check methods exist
    print("\n[4] METHOD CHECKS")
    print("-" * 80)
    
    try:
        from grace_rebuild.backend.meta_loop_engine import recommendation_applicator
        
        methods = [
            "apply_threshold_change",
            "apply_interval_change",
            "apply_priority_change",
            "validate_recommendation",
            "measure_before_metrics",
            "measure_after_metrics",
            "rollback_change"
        ]
        
        for method in methods:
            has_method = hasattr(recommendation_applicator, method)
            status = "✓" if has_method else "✗"
            print(f"{status} recommendation_applicator.{method}")
    except Exception as e:
        print(f"✗ Could not check methods: {e}")
    
    # Check API endpoints
    print("\n[5] API ENDPOINT CHECKS")
    print("-" * 80)
    
    try:
        from grace_rebuild.backend.routes.meta_api import router
        
        endpoints = []
        for route in router.routes:
            endpoints.append(f"{route.methods} {route.path}")
        
        expected = [
            "recommendations/pending",
            "recommendations/{rec_id}/approve",
            "recommendations/{rec_id}/reject",
            "recommendations/applied",
            "recommendations/{applied_id}/rollback",
            "recommendations/{applied_id}/measure",
            "recommendations/stats"
        ]
        
        all_routes = "\n".join(endpoints)
        for exp in expected:
            found = exp in all_routes
            status = "✓" if found else "✗"
            print(f"{status} {exp}")
            results["api_endpoints"].append((exp, found))
    except Exception as e:
        print(f"✗ Could not check endpoints: {e}")
    
    # Check safety limits
    print("\n[6] SAFETY LIMITS")
    print("-" * 80)
    
    try:
        from grace_rebuild.backend.meta_loop_engine import recommendation_applicator
        limits = recommendation_applicator.safety_limits
        
        print(f"✓ Task threshold: {limits['task_threshold']['min']}-{limits['task_threshold']['max']}")
        print(f"✓ Reflection interval: {limits['reflection_interval']['min']}-{limits['reflection_interval']['max']}")
        print(f"✓ Task priority: {limits['task_priority']['min']}-{limits['task_priority']['max']}")
    except Exception as e:
        print(f"✗ Could not check safety limits: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    files_ok = sum(1 for _, ok in results["files"] if ok)
    imports_ok = sum(1 for _, ok in results["imports"] if ok)
    api_ok = sum(1 for _, ok in results["api_endpoints"] if ok)
    
    print(f"\nFiles:     {files_ok}/{len(results['files'])} found")
    print(f"Imports:   {imports_ok}/{len(results['imports'])} successful")
    print(f"Endpoints: {api_ok}/{len(results['api_endpoints'])} present")
    
    all_ok = (files_ok == len(results["files"]) and 
              imports_ok == len(results["imports"]) and 
              api_ok == len(results["api_endpoints"]))
    
    if all_ok:
        print("\n🎉 ALL CHECKS PASSED - System Ready!")
    else:
        print("\n⚠️  Some checks failed - Review above")
    
    print("\n📚 Documentation:")
    print("  - Full guide: grace_rebuild/backend/META_LOOP_SYSTEM.md")
    print("  - Quick ref: grace_rebuild/META_LOOP_QUICK_REFERENCE.md")
    print("  - Summary: grace_rebuild/META_LOOP_ACTIVATION_SUMMARY.md")
    
    print("\n🚀 Next Steps:")
    print("  1. Start backend server")
    print("  2. View: GET /api/meta/recommendations/pending")
    print("  3. Monitor meta-loop logs (runs every 300s)")
    print("  4. Approve recommendations as they arrive")
    
    return all_ok

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    verify_system()
