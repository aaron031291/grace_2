"""Meta Loop - Re-export from workflow_engines module"""

from typing import Any as _Any

MetaLoopConfig: _Any
MetaAnalysis: _Any
MetaMetaEvaluation: _Any
MetaLoopEngine: _Any
meta_loop_engine: _Any
meta_meta_engine: _Any


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'MetaLoopConfig':
        from .workflow_engines.meta_loop import MetaLoopConfig
        return MetaLoopConfig
    elif name == 'MetaAnalysis':
        from .workflow_engines.meta_loop import MetaAnalysis
        return MetaAnalysis
    elif name == 'MetaMetaEvaluation':
        from .workflow_engines.meta_loop import MetaMetaEvaluation
        return MetaMetaEvaluation
    elif name == 'MetaLoopEngine':
        from .workflow_engines.meta_loop import MetaLoopEngine
        return MetaLoopEngine
    elif name == 'meta_loop_engine':
        try:
            from .workflow_engines.meta_loop_engine import meta_loop_engine
            return meta_loop_engine
        except ImportError:
            return None
    elif name == 'meta_meta_engine':
        try:
            from .workflow_engines.meta_loop_engine import meta_meta_engine
            return meta_meta_engine
        except ImportError:
            return None
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    'MetaLoopConfig',
    'MetaAnalysis',
    'MetaMetaEvaluation',
    'MetaLoopEngine',
    'meta_loop_engine',
    'meta_meta_engine'
]
