"""
Structured Logging System for Grace
Outputs JSON logs with correlation IDs, subsystem tracking, and timeline integration
"""

import logging
import json
import sys
from datetime import datetime
from typing import Optional
from contextvars import ContextVar

# Context variables for correlation
run_id_ctx: ContextVar[Optional[str]] = ContextVar('run_id', default=None)
playbook_id_ctx: ContextVar[Optional[str]] = ContextVar('playbook_id', default=None)
verification_id_ctx: ContextVar[Optional[str]] = ContextVar('verification_id', default=None)
request_id_ctx: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class StructuredFormatter(logging.Formatter):
    """JSON formatter with correlation IDs"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        
        # Base structure
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add correlation IDs if present
        run_id = run_id_ctx.get()
        if run_id:
            log_data["run_id"] = run_id
        
        playbook_id = playbook_id_ctx.get()
        if playbook_id:
            log_data["playbook_id"] = playbook_id
        
        verification_id = verification_id_ctx.get()
        if verification_id:
            log_data["verification_id"] = verification_id
        
        request_id = request_id_ctx.get()
        if request_id:
            log_data["request_id"] = request_id
        
        # Add subsystem if in record
        if hasattr(record, 'subsystem'):
            log_data["subsystem"] = record.subsystem
        
        # Add event type if present
        if hasattr(record, 'event_type'):
            log_data["event_type"] = record.event_type
        
        # Add details/payload
        if hasattr(record, 'details'):
            log_data["details"] = record.details
        
        if hasattr(record, 'payload'):
            log_data["payload"] = record.payload
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields from extra
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName', 
                          'levelname', 'levelno', 'lineno', 'module', 'msecs', 
                          'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                          'subsystem', 'event_type', 'details', 'payload']:
                log_data[key] = value
        
        return json.dumps(log_data)


def setup_structured_logging(log_file: str = "logs/backend.log", enable: bool = True):
    """Setup structured JSON logging"""
    
    if not enable:
        # Use traditional logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return
    
    # Create structured formatter
    formatter = StructuredFormatter()
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Console handler (also structured for parsing)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_structured_logger(name: str, subsystem: str = None):
    """Get logger with subsystem context"""
    logger = logging.getLogger(name)
    
    if subsystem:
        # Wrap logger to inject subsystem
        class SubsystemLogger:
            def __init__(self, logger, subsystem):
                self._logger = logger
                self._subsystem = subsystem
            
            def _log(self, level, msg, *args, **kwargs):
                extra = kwargs.get('extra', {})
                extra['subsystem'] = self._subsystem
                kwargs['extra'] = extra
                getattr(self._logger, level)(msg, *args, **kwargs)
            
            def debug(self, msg, *args, **kwargs):
                self._log('debug', msg, *args, **kwargs)
            
            def info(self, msg, *args, **kwargs):
                self._log('info', msg, *args, **kwargs)
            
            def warning(self, msg, *args, **kwargs):
                self._log('warning', msg, *args, **kwargs)
            
            def error(self, msg, *args, **kwargs):
                self._log('error', msg, *args, **kwargs)
            
            def critical(self, msg, *args, **kwargs):
                self._log('critical', msg, *args, **kwargs)
        
        return SubsystemLogger(logger, subsystem)
    
    return logger


# Helper functions to set correlation context

def set_run_context(run_id: str):
    """Set run ID for correlation"""
    run_id_ctx.set(run_id)


def set_playbook_context(playbook_id: str):
    """Set playbook ID for correlation"""
    playbook_id_ctx.set(playbook_id)


def set_verification_context(verification_id: str):
    """Set verification ID for correlation"""
    verification_id_ctx.set(verification_id)


def set_request_context(request_id: str):
    """Set request ID for correlation"""
    request_id_ctx.set(request_id)


def clear_context():
    """Clear all correlation context"""
    run_id_ctx.set(None)
    playbook_id_ctx.set(None)
    verification_id_ctx.set(None)
    request_id_ctx.set(None)
