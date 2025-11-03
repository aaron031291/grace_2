"""
Domain Command Handlers for CLI
Routes CLI commands to backend API endpoints
"""

import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


async def execute_core_command(action: str, backend_url: str):
    """Execute core domain commands"""
    async with httpx.AsyncClient() as client:
        try:
            if action == 'heartbeat':
                response = await client.get(f"{backend_url}/api/core/heartbeat")
                data = response.json()
                console.print(f"[green]✓[/green] Platform is alive")
                console.print(f"  Uptime: {data.get('uptime', 0):.2%}")
            
            elif action == 'governance':
                response = await client.get(f"{backend_url}/api/core/governance")
                data = response.json()
                console.print(f"[bold]Governance Score:[/bold] {data.get('governance_score', 0):.1%}")
                console.print(f"  Active Policies: {data.get('active_policies', 0)}")
            
            elif action == 'self-heal':
                response = await client.post(f"{backend_url}/api/core/self-heal")
                data = response.json()
                console.print(f"[green]✓[/green] Self-healing triggered")
            
            elif action == 'policies':
                response = await client.get(f"{backend_url}/api/core/policies")
                data = response.json()
                policies = data.get('policies', [])
                console.print(f"[bold]{len(policies)} Active Policies[/bold]")
                for p in policies[:10]:
                    console.print(f"  • {p}")
            
            elif action == 'verify':
                response = await client.get(f"{backend_url}/api/core/verify")
                data = response.json()
                console.print(f"[bold]Verification Audit[/bold]")
                console.print(f"  Total: {data.get('count', 0)}")
                console.print(f"  Failures: {data.get('failures', 0)}")
            
            else:
                console.print(f"[yellow]Unknown action: {action}[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


async def execute_transcendence_command(action: str, args, backend_url: str):
    """Execute transcendence domain commands"""
    async with httpx.AsyncClient() as client:
        try:
            if action == 'plan':
                task = ' '.join(args.task) if hasattr(args, 'task') else ''
                response = await client.post(
                    f"{backend_url}/api/transcendence/plan",
                    json={"task_description": task, "context": {}}
                )
                data = response.json()
                console.print(f"[green]✓[/green] Task planned")
                console.print(f"  Task: {task}")
            
            elif action == 'generate':
                spec = ' '.join(args.spec) if hasattr(args, 'spec') else ''
                response = await client.post(
                    f"{backend_url}/api/transcendence/generate",
                    json={"specification": spec, "language": "python"}
                )
                data = response.json()
                console.print(f"[green]✓[/green] Code generated")
                console.print(f"  Quality: {data.get('quality_score', 0):.1%}")
                if 'code' in data:
                    console.print("\n[bold]Generated Code:[/bold]")
                    console.print(data['code'][:500] + "..." if len(data.get('code', '')) > 500 else data.get('code', ''))
            
            elif action == 'memory':
                query = ' '.join(args.query) if hasattr(args, 'query') else ''
                response = await client.post(
                    f"{backend_url}/api/transcendence/memory/search",
                    json={"query": query, "limit": 10}
                )
                data = response.json()
                results = data.get('results', [])
                console.print(f"[bold]Memory Search:[/bold] {len(results)} results")
                for r in results[:5]:
                    console.print(f"  • {r}")
            
            else:
                console.print(f"[yellow]Unknown action: {action}[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


async def execute_security_command(action: str, args, backend_url: str):
    """Execute security domain commands"""
    async with httpx.AsyncClient() as client:
        try:
            if action == 'scan':
                path = args.path if hasattr(args, 'path') else '.'
                response = await client.post(
                    f"{backend_url}/api/security/scan",
                    json={"path": path, "deep": False}
                )
                data = response.json()
                threats = data.get('threats_found', 0)
                
                if threats == 0:
                    console.print(f"[green]✓[/green] No threats found")
                else:
                    console.print(f"[yellow]⚠[/yellow] {threats} threats detected")
                
                console.print(f"  Coverage: {data.get('coverage', 0):.1%}")
            
            elif action == 'rules':
                response = await client.get(f"{backend_url}/api/security/rules")
                data = response.json()
                rules = data.get('rules', [])
                console.print(f"[bold]{len(rules)} Security Rules[/bold]")
                for r in rules[:10]:
                    console.print(f"  • {r}")
            
            elif action == 'alerts':
                response = await client.get(f"{backend_url}/api/security/alerts")
                data = response.json()
                alerts = data.get('alerts', [])
                console.print(f"[bold]{len(alerts)} Active Alerts[/bold]")
                for a in alerts[:10]:
                    console.print(f"  • {a}")
            
            elif action == 'quarantine':
                response = await client.get(f"{backend_url}/api/security/quarantined")
                data = response.json()
                items = data.get('quarantined_items', [])
                console.print(f"[bold]{len(items)} Quarantined Items[/bold]")
                for item in items[:10]:
                    console.print(f"  • {item}")
            
            else:
                console.print(f"[yellow]Unknown action: {action}[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
