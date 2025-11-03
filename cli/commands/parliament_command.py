"""Parliament CLI Commands

Command-line interface for Parliament governance system.
"""

import asyncio
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from datetime import datetime

console = Console()

@click.group()
def parliament():
    """Parliament governance and voting system"""
    pass

@parliament.command()
@click.option('--status', '-s', help='Filter by status (voting, approved, rejected, expired)')
@click.option('--committee', '-c', help='Filter by committee')
@click.option('--limit', '-l', default=20, help='Number of sessions to show')
def sessions(status, committee, limit):
    """List parliament voting sessions"""
    
    async def _list_sessions():
        try:
            from backend.parliament_engine import parliament_engine
            
            sessions_list = await parliament_engine.list_sessions(
                status=status,
                committee=committee,
                limit=limit
            )
            
            if not sessions_list:
                console.print("[yellow]No sessions found[/yellow]")
                return
            
            table = Table(title=f"Parliament Sessions ({len(sessions_list)})", show_header=True)
            table.add_column("Session ID", style="cyan", no_wrap=True, width=12)
            table.add_column("Policy", style="magenta")
            table.add_column("Action", style="blue")
            table.add_column("Status", style="bold")
            table.add_column("Committee", style="green")
            table.add_column("Votes", style="yellow", justify="center")
            table.add_column("Outcome", style="bold")
            table.add_column("Created", style="dim")
            
            for s in sessions_list:
                session_id_short = s["session_id"][:8]
                
                # Color status
                status_str = s["status"]
                if status_str == "approved":
                    status_display = f"[green]{status_str}[/green]"
                elif status_str == "rejected":
                    status_display = f"[red]{status_str}[/red]"
                elif status_str == "expired":
                    status_display = f"[dim]{status_str}[/dim]"
                else:
                    status_display = f"[yellow]{status_str}[/yellow]"
                
                # Outcome
                outcome_str = s.get("outcome", "-") or "-"
                if outcome_str == "approved":
                    outcome_display = f"[green]✓ {outcome_str}[/green]"
                elif outcome_str == "rejected":
                    outcome_display = f"[red]✗ {outcome_str}[/red]"
                else:
                    outcome_display = f"[dim]{outcome_str}[/dim]"
                
                created_at = s.get("created_at", "")
                if created_at:
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_str = created_dt.strftime("%Y-%m-%d %H:%M")
                else:
                    created_str = "-"
                
                table.add_row(
                    session_id_short,
                    s["policy_name"][:30],
                    s["action_type"][:20],
                    status_display,
                    s["committee"],
                    s["votes"],
                    outcome_display,
                    created_str
                )
            
            console.print(table)
            console.print(f"\n[dim]Use 'grace parliament session <id>' for details[/dim]")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_list_sessions())

@parliament.command()
@click.argument('session_id')
def session(session_id):
    """View detailed session information"""
    
    async def _get_session():
        try:
            from backend.parliament_engine import parliament_engine
            
            session_data = await parliament_engine.get_session(session_id)
            
            if not session_data:
                console.print(f"[red]Session not found: {session_id}[/red]")
                return
            
            # Session details panel
            details_content = f"""
[bold]Session ID:[/bold] {session_data['session_id']}
[bold]Policy:[/bold] {session_data['policy_name']}
[bold]Action:[/bold] {session_data['action_type']}
[bold]Category:[/bold] {session_data.get('category', 'N/A')}
[bold]Resource:[/bold] {session_data.get('resource', 'N/A')}
[bold]Actor:[/bold] {session_data['actor']}
[bold]Committee:[/bold] {session_data['committee']}
[bold]Risk Level:[/bold] {session_data['risk_level']}
[bold]Status:[/bold] {session_data['status']}
[bold]Quorum:[/bold] {session_data['total_votes']}/{session_data['quorum_required']}
[bold]Threshold:[/bold] {session_data['approval_threshold']*100}%
"""
            
            if session_data.get('decision_reason'):
                details_content += f"\n[bold]Decision:[/bold] {session_data['decision_reason']}"
            
            console.print(Panel(details_content, title="Session Details", border_style="blue"))
            
            # Vote tallies
            approve = session_data['votes_approve']
            reject = session_data['votes_reject']
            abstain = session_data['votes_abstain']
            total = session_data['total_votes']
            
            vote_summary = f"""
[green]✓ Approve:[/green] {approve}
[red]✗ Reject:[/red] {reject}
[yellow]○ Abstain:[/yellow] {abstain}
[bold]Total:[/bold] {total}
"""
            console.print(Panel(vote_summary, title="Vote Tally", border_style="yellow"))
            
            # Votes table
            if session_data.get('votes'):
                votes_table = Table(title="Individual Votes", show_header=True)
                votes_table.add_column("Member", style="cyan")
                votes_table.add_column("Vote", style="bold", justify="center")
                votes_table.add_column("Confidence", justify="center")
                votes_table.add_column("Automated", justify="center")
                votes_table.add_column("Reason", style="dim")
                votes_table.add_column("Time", style="dim")
                
                for v in session_data['votes']:
                    vote_str = v['vote']
                    if vote_str == "approve":
                        vote_display = "[green]✓ Approve[/green]"
                    elif vote_str == "reject":
                        vote_display = "[red]✗ Reject[/red]"
                    else:
                        vote_display = "[yellow]○ Abstain[/yellow]"
                    
                    confidence = v.get('confidence')
                    conf_display = f"{confidence*100:.0f}%" if confidence else "-"
                    
                    automated = "🤖 Yes" if v.get('automated') else "👤 No"
                    
                    reason = v.get('reason', '')[:50] or '-'
                    
                    created_at = v.get('created_at', '')
                    if created_at:
                        created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        time_str = created_dt.strftime("%H:%M:%S")
                    else:
                        time_str = "-"
                    
                    votes_table.add_row(
                        v['display_name'],
                        vote_display,
                        conf_display,
                        automated,
                        reason,
                        time_str
                    )
                
                console.print(votes_table)
            
            # Hunter alerts if any
            if session_data.get('hunter_alerts'):
                alerts_content = "\n".join([
                    f"[{alert.get('severity', 'unknown')}] {alert.get('rule_name', 'Unknown')}"
                    for alert in session_data['hunter_alerts']
                ])
                console.print(Panel(alerts_content, title="🔒 Security Alerts", border_style="red"))
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_get_session())

@parliament.command()
@click.argument('session_id')
@click.option('--approve', '-a', 'vote_choice', flag_value='approve', help='Vote to approve')
@click.option('--reject', '-r', 'vote_choice', flag_value='reject', help='Vote to reject')
@click.option('--abstain', '-x', 'vote_choice', flag_value='abstain', help='Vote to abstain')
@click.option('--reason', '-m', help='Reason for vote')
def vote(session_id, vote_choice, reason):
    """Cast your vote on a session"""
    
    if not vote_choice:
        console.print("[red]Please specify --approve, --reject, or --abstain[/red]")
        return
    
    async def _cast_vote():
        try:
            from backend.parliament_engine import parliament_engine
            from backend.auth import get_current_user_sync
            
            # Get current user (would normally come from auth context)
            # For CLI, we'll use a default or read from config
            member_id = "admin"  # TODO: Get from CLI auth context
            
            result = await parliament_engine.cast_vote(
                session_id=session_id,
                member_id=member_id,
                vote=vote_choice,
                reason=reason,
                automated=False
            )
            
            vote_emoji = {"approve": "✓", "reject": "✗", "abstain": "○"}[vote_choice]
            vote_color = {"approve": "green", "reject": "red", "abstain": "yellow"}[vote_choice]
            
            console.print(f"\n[{vote_color}]{vote_emoji} Vote cast: {vote_choice.upper()}[/{vote_color}]")
            console.print(f"[dim]Session: {session_id}[/dim]")
            
            if result.get('decision'):
                decision = result['decision']
                if decision.get('status') in ['approved', 'rejected']:
                    console.print(f"\n[bold]🏛️ DECISION REACHED[/bold]")
                    console.print(f"Outcome: [{vote_color}]{decision['outcome']}[/{vote_color}]")
                    console.print(f"Reason: {decision['reason']}")
                else:
                    votes_needed = decision.get('votes_needed', 0)
                    console.print(f"\n[yellow]⏳ Voting continues ({votes_needed} more votes needed)[/yellow]")
            
        except ValueError as e:
            console.print(f"[red]Invalid vote: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_cast_vote())

@parliament.command()
def members():
    """List parliament members"""
    
    async def _list_members():
        try:
            from backend.parliament_engine import parliament_engine
            
            members_list = await parliament_engine.list_members()
            
            if not members_list:
                console.print("[yellow]No members found[/yellow]")
                return
            
            table = Table(title=f"Parliament Members ({len(members_list)})", show_header=True)
            table.add_column("Member ID", style="cyan")
            table.add_column("Name", style="bold")
            table.add_column("Type", style="magenta")
            table.add_column("Role", style="green")
            table.add_column("Committees", style="blue")
            table.add_column("Weight", justify="center")
            table.add_column("Votes", justify="center")
            table.add_column("Status", justify="center")
            
            for m in members_list:
                committees_str = ", ".join(m["committees"][:2]) if m["committees"] else "-"
                if len(m["committees"]) > 2:
                    committees_str += f" +{len(m['committees'])-2}"
                
                status = "✓" if m["active"] and not m["suspended"] else "✗"
                status_color = "green" if m["active"] and not m["suspended"] else "red"
                
                table.add_row(
                    m["member_id"],
                    m["display_name"],
                    m["type"],
                    m["role"],
                    committees_str,
                    str(m["vote_weight"]),
                    str(m["total_votes"]),
                    f"[{status_color}]{status}[/{status_color}]"
                )
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_list_members())

@parliament.command()
def stats():
    """Show parliament statistics"""
    
    async def _show_stats():
        try:
            from backend.parliament_engine import parliament_engine
            
            stats_data = await parliament_engine.get_statistics()
            
            # Overall stats panel
            stats_content = f"""
[bold cyan]MEMBERS[/bold cyan]
Total Members: {stats_data['total_members']}
Active Members: {stats_data['active_members']}

[bold yellow]SESSIONS[/bold yellow]
Total Sessions: {stats_data['total_sessions']}
Pending: {stats_data['sessions_pending']}
Approved: [green]{stats_data['sessions_approved']}[/green]
Rejected: [red]{stats_data['sessions_rejected']}[/red]
Expired: [dim]{stats_data['sessions_expired']}[/dim]

[bold green]VOTING[/bold green]
Total Votes Cast: {stats_data['total_votes_cast']}
Approval Rate: {stats_data['approval_rate']*100:.1f}%
"""
            
            console.print(Panel(stats_content, title="🏛️ Parliament Statistics", border_style="blue"))
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_show_stats())

@parliament.command()
@click.option('--auto-vote/--no-auto-vote', default=False, help='Auto-vote on pending sessions')
def monitor(auto_vote):
    """Monitor pending sessions (Grace agent)"""
    
    async def _monitor():
        try:
            from backend.grace_parliament_agent import grace_voting_agent
            
            console.print("[cyan]Monitoring parliament sessions...[/cyan]")
            
            result = await grace_voting_agent.monitor_sessions(auto_vote=auto_vote)
            
            console.print(f"\n[bold]Session Monitoring Results[/bold]")
            console.print(f"Total Sessions: {result['total_sessions']}")
            console.print(f"Voted: [green]{result['voted']}[/green]")
            console.print(f"Skipped: [yellow]{result['skipped']}[/yellow]")
            
            if result.get('votes'):
                table = Table(title="Grace Votes Cast", show_header=True)
                table.add_column("Session ID", style="cyan", width=12)
                table.add_column("Vote", style="bold", justify="center")
                table.add_column("Confidence", justify="center")
                table.add_column("Reasoning", style="dim")
                
                for v in result['votes']:
                    session_short = v['session_id'][:8]
                    vote_str = v['vote']
                    if vote_str == "approve":
                        vote_display = "[green]✓[/green]"
                    elif vote_str == "reject":
                        vote_display = "[red]✗[/red]"
                    else:
                        vote_display = "[yellow]○[/yellow]"
                    
                    conf = v['confidence']
                    conf_display = f"{conf*100:.0f}%"
                    
                    reasoning = "; ".join(v['reasoning'][:2])[:60]
                    
                    table.add_row(session_short, vote_display, conf_display, reasoning)
                
                console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_monitor())

if __name__ == '__main__':
    parliament()
