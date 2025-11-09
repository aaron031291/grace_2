"""
Full Autonomy Mode
Grace operates with maximum autonomy under governance constraints
"""

import asyncio
from typing import Dict, Any
from datetime import datetime
import logging

from .autonomous_code_healer import code_healer
from .log_based_healer import log_based_healer
from .ml_healing import ml_healing, dl_healing
from .auto_commit import auto_commit
from .governance_framework import governance_framework
from .immutable_log import ImmutableLog

logger = logging.getLogger(__name__)


class FullAutonomyMode:
    """
    Coordinates all autonomous systems for maximum self-healing capability
    
    When enabled, Grace can:
    - Detect errors autonomously
    - Generate fixes autonomously  
    - Apply fixes autonomously (with governance)
    - Commit fixes autonomously
    - Learn from outcomes autonomously
    """
    
    def __init__(self):
        self.enabled = False
        self.autonomy_tier = 2  # Default tier (0-3)
        self.immutable_log = ImmutableLog()
        
        # Autonomy settings per tier
        self.tier_settings = {
            0: {  # Manual
                'auto_detect': True,
                'auto_propose': True,
                'auto_apply': False,
                'auto_commit': False,
                'require_approval_all': True
            },
            1: {  # Supervised
                'auto_detect': True,
                'auto_propose': True,
                'auto_apply': True,  # Apply low-risk only
                'auto_commit': False,
                'require_approval_all': False
            },
            2: {  # Semi-Autonomous
                'auto_detect': True,
                'auto_propose': True,
                'auto_apply': True,  # Apply low & medium risk
                'auto_commit': True,  # Commit low-risk fixes
                'require_approval_all': False
            },
            3: {  # Full Autonomy
                'auto_detect': True,
                'auto_propose': True,
                'auto_apply': True,  # Apply all with governance
                'auto_commit': True,  # Commit all fixes
                'require_approval_all': False
            }
        }
    
    async def enable(self, tier: int = 2):
        """
        Enable full autonomy mode
        
        Args:
            tier: Autonomy tier (0=Manual, 1=Supervised, 2=Semi-Auto, 3=Full)
        """
        
        if tier < 0 or tier > 3:
            logger.error(f"[AUTONOMY] Invalid tier: {tier}")
            return False
        
        self.autonomy_tier = tier
        self.enabled = True
        
        settings = self.tier_settings[tier]
        
        # Configure code healer
        code_healer.auto_apply = settings['auto_apply']
        
        # Configure auto-commit
        auto_commit.auto_commit_enabled = settings['auto_commit']
        auto_commit.require_approval = settings['require_approval_all']
        
        # Log to immutable log
        await self.immutable_log.append(
            actor="grace",
            action="autonomy_enabled",
            resource=f"tier_{tier}",
            subsystem="full_autonomy",
            payload={
                'tier': tier,
                'settings': settings
            },
            result="enabled"
        )
        
        logger.info(f"[AUTONOMY] ✅ Full Autonomy Mode enabled (Tier {tier})")
        logger.info(f"[AUTONOMY]    Auto-detect: {settings['auto_detect']}")
        logger.info(f"[AUTONOMY]    Auto-propose: {settings['auto_propose']}")
        logger.info(f"[AUTONOMY]    Auto-apply: {settings['auto_apply']}")
        logger.info(f"[AUTONOMY]    Auto-commit: {settings['auto_commit']}")
        
        return True
    
    async def disable(self):
        """Disable full autonomy mode"""
        
        if not self.enabled:
            return
        
        self.enabled = False
        
        # Revert to safe defaults
        code_healer.auto_apply = False
        auto_commit.auto_commit_enabled = False
        auto_commit.require_approval = True
        
        await self.immutable_log.append(
            actor="grace",
            action="autonomy_disabled",
            resource="all_systems",
            subsystem="full_autonomy",
            payload={'previous_tier': self.autonomy_tier},
            result="disabled"
        )
        
        logger.info("[AUTONOMY] 🛑 Full Autonomy Mode disabled")
    
    async def set_tier(self, new_tier: int):
        """Change autonomy tier"""
        
        if new_tier < 0 or new_tier > 3:
            return False
        
        old_tier = self.autonomy_tier
        
        # Check governance for tier change
        approval = await governance_framework.check_action(
            actor="grace",
            action="change_autonomy_tier",
            resource=f"tier_{old_tier}_to_{new_tier}",
            context={'old_tier': old_tier, 'new_tier': new_tier},
            confidence=0.9
        )
        
        if not approval.get("approved", False):
            logger.warning(f"[AUTONOMY] Tier change requires approval: {old_tier} → {new_tier}")
            return False
        
        # Re-enable with new tier
        await self.disable()
        await self.enable(new_tier)
        
        logger.info(f"[AUTONOMY] 🔄 Tier changed: {old_tier} → {new_tier}")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get autonomy status"""
        return {
            'enabled': self.enabled,
            'tier': self.autonomy_tier,
            'tier_name': ['Manual', 'Supervised', 'Semi-Autonomous', 'Full Autonomy'][self.autonomy_tier],
            'settings': self.tier_settings[self.autonomy_tier] if self.enabled else {},
            'systems': {
                'code_healer': {
                    'auto_apply': getattr(code_healer, 'auto_apply', False)
                },
                'auto_commit': auto_commit.get_status()
            }
        }


# Global instance
full_autonomy = FullAutonomyMode()
