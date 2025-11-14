"""
HTM Size Tracker - Payload Size Monitoring and Analysis

Features:
- Track data volume alongside timing
- Calculate throughput (bytes/sec, items/sec)
- Human-readable size formatting
- Size-based task classification
- Bandwidth utilization metrics

Integration:
- Hooks into HTM task creation/completion
- Aggregates size metrics for dashboard
- Enables size-aware scheduling
"""

import os
import sys
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class TaskSizeClass(str, Enum):
    """Task size classifications"""
    TINY = "tiny"          # < 1 KB
    SMALL = "small"        # 1 KB - 1 MB
    MEDIUM = "medium"      # 1 MB - 100 MB
    LARGE = "large"        # 100 MB - 1 GB
    HUGE = "huge"          # 1 GB - 10 GB
    MASSIVE = "massive"    # > 10 GB


@dataclass
class PayloadSize:
    """Structured payload size information"""
    data_size_bytes: int
    input_count: Optional[int] = None
    output_size_bytes: Optional[int] = None
    
    def to_human_readable(self) -> str:
        """Convert bytes to human-readable format"""
        return format_bytes(self.data_size_bytes)
    
    def get_size_class(self) -> TaskSizeClass:
        """Classify task by data volume"""
        return classify_task_size(self.data_size_bytes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "data_size_bytes": self.data_size_bytes,
            "data_size_human": self.to_human_readable(),
            "size_class": self.get_size_class().value,
            "input_count": self.input_count,
            "output_size_bytes": self.output_size_bytes,
            "output_size_human": format_bytes(self.output_size_bytes) if self.output_size_bytes else None
        }


def format_bytes(bytes_value: Optional[int], precision: int = 2) -> str:
    """
    Format bytes into human-readable string
    
    Args:
        bytes_value: Size in bytes
        precision: Decimal places for display
        
    Returns:
        Formatted string (e.g., "1.5 MB", "342 KB")
    """
    if bytes_value is None:
        return "N/A"
    
    if bytes_value == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    size = float(bytes_value)
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    if unit_index == 0:  # Bytes - no decimal
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.{precision}f} {units[unit_index]}"


def parse_bytes(size_str: str) -> int:
    """
    Parse human-readable size string to bytes
    
    Args:
        size_str: String like "1.5 MB", "500 KB"
        
    Returns:
        Size in bytes
    """
    size_str = size_str.strip().upper()
    
    # Extract number and unit
    parts = size_str.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid size format: {size_str}")
    
    try:
        value = float(parts[0])
    except ValueError:
        raise ValueError(f"Invalid numeric value: {parts[0]}")
    
    unit = parts[1]
    
    # Convert to bytes
    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
        "PB": 1024 ** 5
    }
    
    if unit not in multipliers:
        raise ValueError(f"Unknown unit: {unit}")
    
    return int(value * multipliers[unit])


def classify_task_size(data_size_bytes: int) -> TaskSizeClass:
    """
    Classify task size into categories
    
    Args:
        data_size_bytes: Total data size
        
    Returns:
        TaskSizeClass enum
    """
    if data_size_bytes < 1024:  # < 1 KB
        return TaskSizeClass.TINY
    elif data_size_bytes < 1024 ** 2:  # < 1 MB
        return TaskSizeClass.SMALL
    elif data_size_bytes < 100 * 1024 ** 2:  # < 100 MB
        return TaskSizeClass.MEDIUM
    elif data_size_bytes < 1024 ** 3:  # < 1 GB
        return TaskSizeClass.LARGE
    elif data_size_bytes < 10 * 1024 ** 3:  # < 10 GB
        return TaskSizeClass.HUGE
    else:  # >= 10 GB
        return TaskSizeClass.MASSIVE


def calculate_throughput(
    data_size_bytes: int,
    execution_time_ms: float
) -> float:
    """
    Calculate throughput in bytes per second
    
    Args:
        data_size_bytes: Total data processed
        execution_time_ms: Time taken in milliseconds
        
    Returns:
        Bytes per second
    """
    if execution_time_ms <= 0:
        return 0.0
    
    execution_time_seconds = execution_time_ms / 1000.0
    return data_size_bytes / execution_time_seconds


def calculate_items_throughput(
    item_count: int,
    execution_time_ms: float
) -> float:
    """
    Calculate item processing throughput
    
    Args:
        item_count: Number of items processed
        execution_time_ms: Time taken in milliseconds
        
    Returns:
        Items per second
    """
    if execution_time_ms <= 0:
        return 0.0
    
    execution_time_seconds = execution_time_ms / 1000.0
    return item_count / execution_time_seconds


class PayloadSizeCalculator:
    """Calculate payload sizes for different task types"""
    
    @staticmethod
    def for_file(file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except (OSError, FileNotFoundError):
            return 0
    
    @staticmethod
    def for_files(file_paths: List[str]) -> Tuple[int, int]:
        """
        Get total size and count for multiple files
        
        Returns:
            (total_bytes, file_count)
        """
        total_bytes = 0
        valid_count = 0
        
        for path in file_paths:
            try:
                total_bytes += os.path.getsize(path)
                valid_count += 1
            except (OSError, FileNotFoundError):
                continue
        
        return total_bytes, valid_count
    
    @staticmethod
    def for_text(text: str, encoding: str = "utf-8") -> int:
        """Get text size in bytes"""
        return len(text.encode(encoding))
    
    @staticmethod
    def for_json(data: Any) -> int:
        """Get JSON data size in bytes"""
        json_str = json.dumps(data, ensure_ascii=False)
        return len(json_str.encode("utf-8"))
    
    @staticmethod
    def for_tokens(token_count: int, avg_bytes_per_token: float = 4.0) -> int:
        """
        Estimate size from token count
        
        Args:
            token_count: Number of tokens
            avg_bytes_per_token: Average bytes per token (default ~4 for English)
            
        Returns:
            Estimated bytes
        """
        return int(token_count * avg_bytes_per_token)
    
    @staticmethod
    def for_embeddings(
        num_vectors: int,
        dimensions: int = 1536,
        bytes_per_float: int = 4
    ) -> int:
        """
        Calculate embedding storage size
        
        Args:
            num_vectors: Number of embedding vectors
            dimensions: Vector dimensionality (e.g., 1536 for OpenAI)
            bytes_per_float: Bytes per float (4 for float32, 8 for float64)
            
        Returns:
            Total bytes
        """
        return num_vectors * dimensions * bytes_per_float
    
    @staticmethod
    def for_ingestion_job(
        file_paths: List[str],
        include_embeddings: bool = True,
        embedding_dimensions: int = 1536
    ) -> Dict[str, Any]:
        """
        Calculate size metrics for ingestion job
        
        Returns:
            {
                "input_size_bytes": int,
                "input_count": int,
                "estimated_output_bytes": int,  # If embeddings
                "size_class": str
            }
        """
        input_bytes, file_count = PayloadSizeCalculator.for_files(file_paths)
        
        result = {
            "input_size_bytes": input_bytes,
            "input_count": file_count,
            "size_class": classify_task_size(input_bytes).value
        }
        
        if include_embeddings:
            # Estimate: ~10 chunks per file on average
            estimated_chunks = file_count * 10
            result["estimated_output_bytes"] = PayloadSizeCalculator.for_embeddings(
                estimated_chunks, embedding_dimensions
            )
        
        return result


def get_size_recommendations(
    data_size_bytes: int,
    task_type: str
) -> Dict[str, Any]:
    """
    Get recommendations based on task size
    
    Returns:
        {
            "size_class": str,
            "recommended_worker": str,
            "suggested_timeout_ms": int,
            "batch_recommended": bool,
            "warnings": List[str]
        }
    """
    size_class = classify_task_size(data_size_bytes)
    
    recommendations = {
        "size_class": size_class.value,
        "data_size_human": format_bytes(data_size_bytes),
        "warnings": []
    }
    
    # Size-based recommendations
    if size_class == TaskSizeClass.TINY:
        recommendations["recommended_worker"] = "light"
        recommendations["suggested_timeout_ms"] = 5000
        recommendations["batch_recommended"] = True
        
    elif size_class == TaskSizeClass.SMALL:
        recommendations["recommended_worker"] = "standard"
        recommendations["suggested_timeout_ms"] = 30000
        recommendations["batch_recommended"] = True
        
    elif size_class == TaskSizeClass.MEDIUM:
        recommendations["recommended_worker"] = "standard"
        recommendations["suggested_timeout_ms"] = 120000
        recommendations["batch_recommended"] = False
        
    elif size_class == TaskSizeClass.LARGE:
        recommendations["recommended_worker"] = "heavy"
        recommendations["suggested_timeout_ms"] = 600000  # 10 min
        recommendations["batch_recommended"] = False
        recommendations["warnings"].append("Large payload - consider chunking")
        
    elif size_class == TaskSizeClass.HUGE:
        recommendations["recommended_worker"] = "heavy"
        recommendations["suggested_timeout_ms"] = 1800000  # 30 min
        recommendations["batch_recommended"] = False
        recommendations["warnings"].extend([
            "Very large payload - strongly recommend chunking",
            "Consider streaming processing"
        ])
        
    elif size_class == TaskSizeClass.MASSIVE:
        recommendations["recommended_worker"] = "heavy"
        recommendations["suggested_timeout_ms"] = 3600000  # 1 hour
        recommendations["batch_recommended"] = False
        recommendations["warnings"].extend([
            "Massive payload - must chunk or stream",
            "Consider distributed processing",
            "May exceed memory limits"
        ])
    
    return recommendations


def estimate_memory_usage(
    data_size_bytes: int,
    task_type: str = "generic",
    memory_multiplier: float = 3.0
) -> int:
    """
    Estimate memory usage for task
    
    Args:
        data_size_bytes: Input data size
        task_type: Type of task (affects multiplier)
        memory_multiplier: Factor for memory overhead
        
    Returns:
        Estimated memory in bytes
    """
    # Different task types have different memory characteristics
    type_multipliers = {
        "ingestion": 2.0,      # Light processing
        "embedding": 4.0,      # Vector computation
        "analysis": 3.0,       # Medium processing
        "transformation": 5.0, # Heavy processing
        "generic": 3.0
    }
    
    multiplier = type_multipliers.get(task_type, memory_multiplier)
    return int(data_size_bytes * multiplier)


# Convenience functions for common scenarios

def get_ingestion_size(file_paths: List[str]) -> PayloadSize:
    """Quick helper for ingestion tasks"""
    total_bytes, file_count = PayloadSizeCalculator.for_files(file_paths)
    return PayloadSize(
        data_size_bytes=total_bytes,
        input_count=file_count
    )


def get_text_processing_size(texts: List[str]) -> PayloadSize:
    """Quick helper for text processing tasks"""
    total_bytes = sum(PayloadSizeCalculator.for_text(t) for t in texts)
    return PayloadSize(
        data_size_bytes=total_bytes,
        input_count=len(texts)
    )


def get_embedding_size(num_vectors: int, dimensions: int = 1536) -> PayloadSize:
    """Quick helper for embedding tasks"""
    total_bytes = PayloadSizeCalculator.for_embeddings(num_vectors, dimensions)
    return PayloadSize(
        data_size_bytes=total_bytes,
        input_count=num_vectors,
        output_size_bytes=total_bytes
    )
