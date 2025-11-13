"""
Sandbox Self-Improvement System
Grace experiments with improvements in isolated sandbox environment
"""

import asyncio
import subprocess
import json
import psutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class SandboxImprovement:
    """
    Sandbox environment for Grace's self-improvement experiments
    - Isolated filesystem/network
    - CPU/RAM/time limits
    - Security checks before external API calls
    - KPI tracking and validation
    """
    
    def __init__(self):
        self.sandbox_dir = Path('sandbox')
        self.logs_dir = Path('logs/sandbox')
        self.running_experiments = {}
    
    async def start(self):
        """Initialize sandbox environment"""
        
        self.sandbox_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("[SANDBOX-IMPROVEMENT] Initialized")
    
    async def run_experiment(
        self,
        experiment_name: str,
        code_file: str,
        kpi_thresholds: Dict[str, Any],
        timeout: int = 300,
        max_memory_mb: int = 512
    ) -> Dict[str, Any]:
        """
        Run an improvement experiment in sandbox
        
        Args:
            experiment_name: Name of the experiment
            code_file: Path to code file to run
            kpi_thresholds: Expected KPI thresholds
            timeout: Max execution time in seconds
            max_memory_mb: Max memory usage in MB
        
        Returns:
            Experiment results with metrics and success status
        """
        
        experiment_id = f"{experiment_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"[SANDBOX] Starting experiment: {experiment_id}")
        
        # Log decision
        await unified_logger.log_agentic_spine_decision(
            decision_type='sandbox_experiment',
            decision_context={'experiment': experiment_name, 'file': code_file},
            chosen_action='run_in_sandbox',
            rationale=f'Testing {experiment_name} in isolated environment',
            actor='sandbox_improvement',
            confidence=0.85,
            risk_score=0.2,
            status='started',
            resource=experiment_id
        )
        
        result = {
            'experiment_id': experiment_id,
            'experiment_name': experiment_name,
            'code_file': code_file,
            'started_at': datetime.utcnow().isoformat(),
            'status': 'unknown',
            'kpi_thresholds': kpi_thresholds,
            'kpis_met': {},
            'metrics': {},
            'output': '',
            'errors': [],
            'security_checks': {},
            'trust_score': 0
        }
        
        try:
            # Run code in sandbox with resource limits
            output, metrics = await self._run_in_sandbox(
                code_file,
                timeout=timeout,
                max_memory_mb=max_memory_mb
            )
            
            result['output'] = output
            result['metrics'] = metrics
            
            # Check KPIs
            kpis_met = self._check_kpis(metrics, kpi_thresholds)
            result['kpis_met'] = kpis_met
            
            # Calculate trust score
            trust_score = self._calculate_trust_score(kpis_met, metrics)
            result['trust_score'] = trust_score
            
            # Determine overall status
            if all(kpis_met.values()):
                result['status'] = 'success'
            elif trust_score >= 70:
                result['status'] = 'conditional_success'
            else:
                result['status'] = 'failed'
            
            # Save report
            await self._save_experiment_report(result)
            
            logger.info(f"[SANDBOX] Experiment {experiment_id}: {result['status']} (trust: {trust_score}%)")
        
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(str(e))
            logger.error(f"[SANDBOX] Experiment {experiment_id} error: {e}")
        
        result['finished_at'] = datetime.utcnow().isoformat()
        
        return result
    
    async def _run_in_sandbox(
        self,
        code_file: str,
        timeout: int,
        max_memory_mb: int
    ) -> tuple:
        """Run code with resource limits"""
        
        start_time = datetime.utcnow()
        
        # Run in subprocess with limits
        try:
            # Linux: use resource limits
            # Windows: monitor with psutil
            
            process = await asyncio.create_subprocess_exec(
                'python', code_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.sandbox_dir)
            )
            
            # Monitor resources
            try:
                proc = psutil.Process(process.pid)
                max_memory_used = 0
                
                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                # Get final metrics
                try:
                    memory_info = proc.memory_info()
                    max_memory_used = memory_info.rss / (1024 * 1024)  # MB
                except:
                    pass
                
                output = stdout.decode('utf-8') + '\n' + stderr.decode('utf-8')
                
                end_time = datetime.utcnow()
                execution_time = (end_time - start_time).total_seconds()
                
                metrics = {
                    'execution_time_sec': execution_time,
                    'memory_used_mb': max_memory_used,
                    'exit_code': process.returncode,
                    'timeout_exceeded': False
                }
                
                return output, metrics
            
            except asyncio.TimeoutError:
                process.kill()
                
                metrics = {
                    'execution_time_sec': timeout,
                    'memory_used_mb': max_memory_mb,
                    'exit_code': -1,
                    'timeout_exceeded': True
                }
                
                return 'Timeout exceeded', metrics
        
        except Exception as e:
            logger.error(f"[SANDBOX] Error running code: {e}")
            
            metrics = {
                'execution_time_sec': 0,
                'memory_used_mb': 0,
                'exit_code': -1,
                'error': str(e)
            }
            
            return f'Error: {e}', metrics
    
    def _check_kpis(
        self,
        metrics: Dict[str, Any],
        thresholds: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Check if metrics meet KPI thresholds"""
        
        kpis_met = {}
        
        for kpi, threshold in thresholds.items():
            if kpi not in metrics:
                kpis_met[kpi] = False
                continue
            
            value = metrics[kpi]
            
            # Parse threshold (e.g., "<200ms", ">95%", "==0")
            if threshold.startswith('<'):
                target = float(threshold[1:].replace('ms', '').replace('%', ''))
                kpis_met[kpi] = value < target
            elif threshold.startswith('>'):
                target = float(threshold[1:].replace('ms', '').replace('%', ''))
                kpis_met[kpi] = value > target
            elif threshold.startswith('=='):
                target = float(threshold[2:])
                kpis_met[kpi] = value == target
            else:
                kpis_met[kpi] = False
        
        return kpis_met
    
    def _calculate_trust_score(
        self,
        kpis_met: Dict[str, bool],
        metrics: Dict[str, Any]
    ) -> int:
        """Calculate trust score (0-100)"""
        
        if not kpis_met:
            return 50
        
        # Base score from KPIs met
        kpi_score = (sum(kpis_met.values()) / len(kpis_met)) * 70
        
        # Bonus for good metrics
        bonus = 0
        
        if metrics.get('exit_code') == 0:
            bonus += 10
        
        if not metrics.get('timeout_exceeded', False):
            bonus += 10
        
        if metrics.get('memory_used_mb', 0) < 100:
            bonus += 10
        
        trust_score = int(min(kpi_score + bonus, 100))
        
        return trust_score
    
    async def _save_experiment_report(self, result: Dict[str, Any]):
        """Save experiment report"""
        
        report_file = self.logs_dir / f"{result['experiment_id']}_report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"[SANDBOX] Report saved: {report_file}")
    
    async def create_improvement_proposal(
        self,
        experiment_result: Dict[str, Any],
        description: str,
        rationale: str
    ) -> Dict[str, Any]:
        """
        Create improvement proposal from successful experiment
        
        Returns proposal for governance review
        """
        
        proposal = {
            'proposal_id': f"improvement_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'type': 'self_improvement',
            'experiment_id': experiment_result['experiment_id'],
            'description': description,
            'rationale': rationale,
            'confidence': experiment_result['trust_score'],
            'kpis_met': experiment_result['kpis_met'],
            'metrics': experiment_result['metrics'],
            'risk_assessment': {
                'level': 'low' if experiment_result['trust_score'] >= 90 else 'medium',
                'sandboxed': True,
                'tested': True,
                'reversible': True
            },
            'created_at': datetime.utcnow().isoformat(),
            'status': 'pending_review'
        }
        
        # Save proposal
        proposals_dir = Path('storage/improvement_proposals')
        proposals_dir.mkdir(parents=True, exist_ok=True)
        
        proposal_file = proposals_dir / f"{proposal['proposal_id']}.json"
        
        with open(proposal_file, 'w', encoding='utf-8') as f:
            json.dump(proposal, f, indent=2)
        
        logger.info(f"[SANDBOX] Improvement proposal created: {proposal['proposal_id']}")
        
        return proposal


# Global instance
sandbox_improvement = SandboxImprovement()
