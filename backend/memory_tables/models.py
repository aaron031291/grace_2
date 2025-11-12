#!/usr/bin/env python3
"""
Base models for Memory Tables system
"""

from sqlmodel import SQLModel
from typing import Any, Dict


class DynamicTableBase(SQLModel):
    """Base class for dynamically generated table models"""
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            # Add custom encoders as needed
        }
