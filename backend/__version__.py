"""Grace Version Information"""

__version__ = "2.1.0"
__version_info__ = (2, 1, 0)

# Release metadata
RELEASE_DATE = "2025-11-17"
RELEASE_NAME = "Guardian Hardened"

# Phase completion status
PHASE_STATUS = {
    "phase_0_baseline": 100,
    "phase_1_guardian": 100,
    "phase_2_rag": 100,
    "phase_3_learning": 100,
    "phase_4_coding": 100,
    "phase_5_ui": 0,
    "phase_6_enterprise": 50,
    "phase_7_saas": 0,
}

# Overall progress to full functionality
OVERALL_PROGRESS = 79  # Percent

# System capabilities
CAPABILITIES = {
    "self_healing": True,
    "guardian_playbooks": 13,
    "mttr_tracking": True,
    "rag_evaluation": True,
    "knowledge_gaps": True,
    "autonomous_coding": True,
    "rate_limiting": True,
    "multi_tenancy": False,  # Phase 7
    "billing": False,  # Phase 7
    "rbac": False,  # Phase 7
}

def get_version_info():
    """Get comprehensive version information"""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "release_date": RELEASE_DATE,
        "release_name": RELEASE_NAME,
        "phase_status": PHASE_STATUS,
        "overall_progress": OVERALL_PROGRESS,
        "capabilities": CAPABILITIES,
    }
