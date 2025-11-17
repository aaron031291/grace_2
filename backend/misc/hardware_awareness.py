"""
Grace Hardware Awareness & Resource Optimization
Understands internal capacity and allocates power intelligently
"""

import psutil
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HardwareProfile:
    """Grace's understanding of her hardware"""
    
    # Known specs from user's build
    KNOWN_SPECS = {
        "cpu": {
            "model": "AMD Ryzen 9 9950X3D",
            "cores": 16,
            "threads": 32,
            "base_clock_ghz": 4.3,
            "boost_clock_ghz": 5.7,
            "tdp_watts": 120
        },
        "gpu": {
            "model": "NVIDIA GeForce RTX 5090",
            "vram_gb": 32,
            "cuda_cores": 21760,
            "tdp_watts": 575,
            "capabilities": ["ml_training", "inference", "ray_tracing", "cuda", "tensor_cores"]
        },
        "ram": {
            "capacity_gb": 64,
            "speed_mhz": 6000,
            "type": "DDR5"
        },
        "storage": {
            "type": "Samsung 990 PRO NVMe",
            "capacity_tb": 4,
            "speed": "PCIe 5.0 x4",
            "read_gbps": 14,
            "write_gbps": 12
        },
        "cooling": {
            "type": "Custom Water Loop",
            "radiators": ["360mm", "360mm"],
            "pump": "Alphacool VPP Apex",
            "thermal_capacity": "high"
        },
        "psu": {
            "wattage": 1000,
            "efficiency": "80+ Gold"
        }
    }
    
    def __init__(self):
        self.current_workload = "idle"
        self.power_mode = "balanced"  # idle, balanced, performance, maximum
        self.gpu_available = False
        self.detect_hardware()
    
    def detect_hardware(self):
        """Detect actual hardware capabilities"""
        try:
            import torch
            self.gpu_available = torch.cuda.is_available()
            if self.gpu_available:
                self.gpu_count = torch.cuda.device_count()
                self.gpu_name = torch.cuda.get_device_name(0)
                logger.info(f"[HARDWARE] GPU Detected: {self.gpu_name}")
        except ImportError:
            logger.info("[HARDWARE] PyTorch not installed - GPU features disabled")
            self.gpu_available = False
    
    def get_current_capacity(self) -> Dict[str, Any]:
        """Get real-time hardware utilization"""
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Estimate power consumption based on load
        cpu_power_estimated = (cpu_percent / 100) * self.KNOWN_SPECS["cpu"]["tdp_watts"]
        
        # GPU power (if in use)
        gpu_power_estimated = 0
        if self.gpu_available and self.current_workload in ["ml_training", "inference"]:
            gpu_power_estimated = self.KNOWN_SPECS["gpu"]["tdp_watts"] * 0.8  # Assume 80% when active
        
        total_power_estimated = cpu_power_estimated + gpu_power_estimated + 50  # +50W for system
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "frequency_mhz": cpu_freq.current if cpu_freq else 0,
                "cores_logical": psutil.cpu_count(),
                "cores_physical": psutil.cpu_count(logical=False),
                "power_watts_estimated": round(cpu_power_estimated, 1),
                "temperature_c": self._get_cpu_temp()
            },
            "memory": {
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2),
                "percent": memory.percent
            },
            "gpu": {
                "available": self.gpu_available,
                "model": self.KNOWN_SPECS["gpu"]["model"],
                "vram_gb": self.KNOWN_SPECS["gpu"]["vram_gb"],
                "active": self.current_workload in ["ml_training", "inference"],
                "power_watts_estimated": round(gpu_power_estimated, 1)
            },
            "storage": {
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2),
                "percent": disk.percent
            },
            "power": {
                "current_watts_estimated": round(total_power_estimated, 1),
                "max_watts": self.KNOWN_SPECS["psu"]["wattage"],
                "headroom_watts": round(self.KNOWN_SPECS["psu"]["wattage"] - total_power_estimated, 1),
                "mode": self.power_mode
            },
            "cooling": {
                "type": self.KNOWN_SPECS["cooling"]["type"],
                "status": "adequate" if cpu_percent < 80 else "high_load"
            }
        }
    
    def _get_cpu_temp(self) -> Optional[float]:
        """Get CPU temperature if available"""
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return round(temps['coretemp'][0].current, 1)
            elif 'cpu_thermal' in temps:
                return round(temps['cpu_thermal'][0].current, 1)
        except:
            pass
        return None
    
    def set_power_mode(self, mode: str, reason: str):
        """
        Adjust power/performance mode
        
        Modes:
        - idle: Minimal power, background tasks only
        - balanced: Normal operation
        - performance: High CPU/GPU for demanding tasks
        - maximum: Full power for ML training, benchmarks
        """
        old_mode = self.power_mode
        self.power_mode = mode
        
        logger.info(f"[HARDWARE] Power mode: {old_mode} → {mode} (reason: {reason})")
        
        # Future: Could adjust CPU governor, GPU power limit, fan curves
    
    async def allocate_for_task(self, task_type: str) -> Dict[str, Any]:
        """
        Intelligently allocate resources for a task
        
        Task types:
        - ml_training: Needs GPU + high CPU
        - inference: GPU preferred
        - code_generation: CPU only
        - data_processing: CPU + RAM
        - idle: Minimal
        """
        
        self.current_workload = task_type
        
        allocation = {
            "task_type": task_type,
            "allocated_at": datetime.utcnow().isoformat()
        }
        
        if task_type == "ml_training":
            self.set_power_mode("maximum", "ML training requires full GPU")
            allocation.update({
                "gpu": True,
                "gpu_memory_gb": 28,  # Reserve most VRAM
                "cpu_threads": 24,  # Reserve most threads
                "ram_gb": 48,  # Reserve most RAM
                "power_budget_watts": 700
            })
        
        elif task_type == "inference":
            self.set_power_mode("performance", "Inference needs GPU")
            allocation.update({
                "gpu": True,
                "gpu_memory_gb": 16,
                "cpu_threads": 8,
                "ram_gb": 16,
                "power_budget_watts": 400
            })
        
        elif task_type == "code_generation":
            self.set_power_mode("balanced", "Code gen is CPU-bound")
            allocation.update({
                "gpu": False,
                "cpu_threads": 8,
                "ram_gb": 8,
                "power_budget_watts": 100
            })
        
        elif task_type == "data_processing":
            self.set_power_mode("balanced", "Data processing")
            allocation.update({
                "gpu": False,
                "cpu_threads": 16,
                "ram_gb": 32,
                "power_budget_watts": 150
            })
        
        else:  # idle
            self.set_power_mode("idle", "No active work")
            allocation.update({
                "gpu": False,
                "cpu_threads": 2,
                "ram_gb": 4,
                "power_budget_watts": 50
            })
        
        logger.info(f"[HARDWARE] Allocated resources for {task_type}: {allocation}")
        return allocation
    
    async def benchmark_when_needed(self, task_type: str) -> Optional[Dict[str, Any]]:
        """
        Run benchmarks ONLY when power is needed
        Don't benchmark during idle/light tasks
        """
        
        if task_type in ["ml_training", "inference"]:
            logger.info(f"[HARDWARE] Running benchmark for {task_type} (high-power task)")
            
            # Activate GPU
            await self.allocate_for_task(task_type)
            
            results = {
                "task_type": task_type,
                "gpu_available": self.gpu_available,
                "estimated_performance": "high" if self.gpu_available else "cpu_only",
                "power_mode": self.power_mode
            }
            
            if self.gpu_available:
                # Could run actual GPU benchmark here
                results["gpu_tflops_estimated"] = 82.6  # RTX 5090 theoretical
                results["gpu_memory_available_gb"] = 32
            
            return results
        else:
            logger.info(f"[HARDWARE] Skipping benchmark for {task_type} (light task)")
            return None
    
    def get_recommendations(self) -> list[str]:
        """Provide hardware optimization recommendations"""
        recommendations = []
        
        capacity = self.get_current_capacity()
        
        if capacity["cpu"]["usage_percent"] > 90:
            recommendations.append("CPU at high load - consider task queuing")
        
        if capacity["memory"]["percent"] > 90:
            recommendations.append("RAM usage high - optimize memory footprint")
        
        if capacity["storage"]["percent"] > 80:
            recommendations.append("Storage >80% - cleanup recommended")
        
        if not self.gpu_available and self.current_workload in ["ml_training", "inference"]:
            recommendations.append("GPU task requested but GPU unavailable - install PyTorch+CUDA")
        
        if capacity["power"]["headroom_watts"] < 200:
            recommendations.append(f"Low power headroom ({capacity['power']['headroom_watts']}W) - reduce concurrent tasks")
        
        return recommendations


# Global instance
hardware_profile = HardwareProfile()
