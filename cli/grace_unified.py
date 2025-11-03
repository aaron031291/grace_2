#!/usr/bin/env python3
"""
Grace Unified CLI - 10-Domain Interface with Real-Time Cognition
Downloads as single tool, exposes all Grace capabilities through domain commands
"""

import argparse
import sys
import asyncio
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        prog="grace",
        description="Grace AI Platform - Your Autonomous Development Partner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Grace operates across 10 integrated domains:
  core          Platform operations, governance, self-healing
  transcendence Agentic development & code generation
  knowledge     Knowledge ingestion & business intelligence
  security      Hunter threat detection & response
  ml            Machine learning lifecycle & deployment
  temporal      Causal reasoning & forecasting
  parliament    Meta-loop governance & optimization
  federation    External integrations & collaboration
  
Real-time cognition monitoring:
  cognition     View live cognitive metrics across all domains
  readiness     Check SaaS commercialization readiness
  
System commands:
  install       Install Grace and dependencies
  start         Start Grace platform services
  status        Quick platform health check
  upgrade       Upgrade to latest version
  
Examples:
  grace cognition               # Watch real-time cognition dashboard
  grace ml deploy --show-conf   # Deploy ML model with confidence
  grace readiness               # Check if ready for SaaS
  grace security scan ./code    # Run Hunter security scan
        """
    )
    
    subparsers = parser.add_subparsers(dest='domain', help='Domain or command')
    
    # System commands
    subparsers.add_parser('install', help='Install Grace dependencies')
    subparsers.add_parser('start', help='Start Grace platform')
    subparsers.add_parser('status', help='Quick health check')
    subparsers.add_parser('upgrade', help='Upgrade Grace')
    
    # Cognition monitoring
    cognition_parser = subparsers.add_parser('cognition', help='Real-time cognition dashboard')
    cognition_parser.add_argument('--backend', default='http://localhost:8000', help='Backend URL')
    cognition_parser.add_argument('--refresh', type=float, default=2.0, help='Refresh rate in seconds')
    
    readiness_parser = subparsers.add_parser('readiness', help='SaaS readiness report')
    readiness_parser.add_argument('--backend', default='http://localhost:8000', help='Backend URL')
    
    # Core domain
    core_parser = subparsers.add_parser('core', help='Platform core operations')
    core_subparsers = core_parser.add_subparsers(dest='action')
    core_subparsers.add_parser('heartbeat', help='Check platform heartbeat')
    core_subparsers.add_parser('governance', help='View governance status')
    core_subparsers.add_parser('self-heal', help='Trigger self-healing')
    
    # Transcendence domain
    trans_parser = subparsers.add_parser('transcendence', help='Agentic development')
    trans_subparsers = trans_parser.add_subparsers(dest='action')
    trans_subparsers.add_parser('plan', help='Create task plan').add_argument('task', nargs='+')
    trans_subparsers.add_parser('generate', help='Generate code').add_argument('spec', nargs='+')
    trans_subparsers.add_parser('memory', help='Search code memory').add_argument('query', nargs='+')
    
    # Knowledge domain
    knowledge_parser = subparsers.add_parser('knowledge', help='Knowledge ingestion')
    knowledge_subparsers = knowledge_parser.add_subparsers(dest='action')
    knowledge_subparsers.add_parser('ingest', help='Ingest knowledge').add_argument('source')
    knowledge_subparsers.add_parser('search', help='Search knowledge').add_argument('query', nargs='+')
    knowledge_subparsers.add_parser('trust', help='View trust scores')
    
    # Security domain
    security_parser = subparsers.add_parser('security', help='Hunter security')
    security_subparsers = security_parser.add_subparsers(dest='action')
    security_subparsers.add_parser('scan', help='Run security scan').add_argument('path')
    security_subparsers.add_parser('rules', help='View security rules')
    security_subparsers.add_parser('alerts', help='View security alerts')
    security_subparsers.add_parser('quarantine', help='View quarantined items')
    
    # ML domain
    ml_parser = subparsers.add_parser('ml', help='ML lifecycle')
    ml_subparsers = ml_parser.add_subparsers(dest='action')
    ml_subparsers.add_parser('train', help='Start training').add_argument('model_name')
    ml_deploy = ml_subparsers.add_parser('deploy', help='Deploy model')
    ml_deploy.add_argument('model_id')
    ml_deploy.add_argument('--show-confidence', action='store_true')
    ml_subparsers.add_parser('list', help='List models')
    ml_subparsers.add_parser('evaluate', help='Evaluate model').add_argument('model_id')
    
    # Temporal domain
    temporal_parser = subparsers.add_parser('temporal', help='Causal reasoning')
    temporal_subparsers = temporal_parser.add_subparsers(dest='action')
    temporal_subparsers.add_parser('graph', help='View causal graph')
    temporal_subparsers.add_parser('simulate', help='Run simulation').add_argument('scenario')
    temporal_subparsers.add_parser('forecast', help='Generate forecast').add_argument('metric')
    
    # Parliament domain
    parliament_parser = subparsers.add_parser('parliament', help='Governance & meta-loop')
    parliament_subparsers = parliament_parser.add_subparsers(dest='action')
    parliament_subparsers.add_parser('vote', help='View active votes')
    parliament_subparsers.add_parser('recommendations', help='Meta-loop recommendations')
    parliament_subparsers.add_parser('compliance', help='Compliance dashboard')
    
    # Federation domain
    federation_parser = subparsers.add_parser('federation', help='External integrations')
    federation_subparsers = federation_parser.add_subparsers(dest='action')
    federation_subparsers.add_parser('connectors', help='List connectors')
    federation_subparsers.add_parser('secrets', help='Manage secrets')
    federation_subparsers.add_parser('api', help='API gateway status')
    
    args = parser.parse_args()
    
    if not args.domain:
        parser.print_help()
        return 0
    
    # Route to appropriate handler
    try:
        if args.domain == 'cognition':
            from cli.commands.cognition_status import show_cognition_status
            asyncio.run(show_cognition_status(args.backend))
        
        elif args.domain == 'readiness':
            from cli.commands.cognition_status import show_readiness_report
            asyncio.run(show_readiness_report(args.backend))
        
        elif args.domain in ['install', 'start', 'status', 'upgrade']:
            from grace_cli import main as old_cli_main
            old_cli_main()
        
        elif args.domain == 'core':
            from cli.commands.domain_commands import execute_core_command
            asyncio.run(execute_core_command(args.action, args.backend if hasattr(args, 'backend') else 'http://localhost:8000'))
        
        elif args.domain == 'transcendence':
            from cli.commands.domain_commands import execute_transcendence_command
            asyncio.run(execute_transcendence_command(args.action, args, args.backend if hasattr(args, 'backend') else 'http://localhost:8000'))
        
        elif args.domain == 'security':
            from cli.commands.domain_commands import execute_security_command
            asyncio.run(execute_security_command(args.action, args, args.backend if hasattr(args, 'backend') else 'http://localhost:8000'))
        
        else:
            print(f"🚧 Domain '{args.domain}' implementation in progress")
            print(f"   Action: {getattr(args, 'action', 'N/A')}")
            print(f"   Use 'grace cognition' to view system status")
            return 1
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
