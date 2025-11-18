"""
Request Tracing - Distributed tracing for request flows
"""

import time
import uuid
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Span:
    """A span represents a unit of work in a trace"""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    
    def finish(self):
        """Mark span as finished"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
    
    def add_tag(self, key: str, value: Any):
        """Add a tag to the span"""
        self.tags[key] = value
    
    def log(self, message: str, **fields):
        """Add a log entry to the span"""
        self.logs.append({
            "timestamp": time.time(),
            "message": message,
            **fields
        })


@dataclass
class Trace:
    """A trace represents the entire journey of a request"""
    trace_id: str
    spans: List[Span] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    
    def add_span(self, span: Span):
        """Add a span to the trace"""
        self.spans.append(span)
    
    def finish(self):
        """Mark trace as finished"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000


class RequestTracer:
    """Manage distributed tracing for requests"""
    
    def __init__(self):
        self.traces: Dict[str, Trace] = {}
        self.active_spans: Dict[str, Span] = {}
    
    def start_trace(self, operation_name: str = "request") -> Trace:
        """Start a new trace"""
        trace_id = str(uuid.uuid4())
        trace = Trace(trace_id=trace_id)
        self.traces[trace_id] = trace
        
        root_span = self.start_span(
            trace_id=trace_id,
            operation_name=operation_name
        )
        
        return trace
    
    def start_span(
        self,
        trace_id: str,
        operation_name: str,
        parent_span_id: Optional[str] = None
    ) -> Span:
        """Start a new span within a trace"""
        span_id = str(uuid.uuid4())
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=time.time()
        )
        
        self.active_spans[span_id] = span
        
        if trace_id in self.traces:
            self.traces[trace_id].add_span(span)
        
        return span
    
    def finish_span(self, span_id: str):
        """Finish a span"""
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span.finish()
            del self.active_spans[span_id]
    
    def finish_trace(self, trace_id: str):
        """Finish a trace"""
        if trace_id in self.traces:
            trace = self.traces[trace_id]
            trace.finish()
            
            for span in list(self.active_spans.values()):
                if span.trace_id == trace_id:
                    self.finish_span(span.span_id)
    
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID"""
        return self.traces.get(trace_id)
    
    def get_span(self, span_id: str) -> Optional[Span]:
        """Get a span by ID"""
        return self.active_spans.get(span_id)
