"""
Tasks command - Task management with kanban board view
"""

import asyncio
from typing import Optional, List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.prompt import Prompt, Confirm
from ..grace_client import GraceAPIClient


class TasksCommand:
    """Task management"""
    
    def __init__(self, client: GraceAPIClient, console: Console):
        self.client = client
        self.console = console
    
    async def execute(self, action: Optional[str] = None, *args):
        """Execute tasks command"""
        if not self.client.is_authenticated():
            self.console.print("[red]Please login first[/red]")
            return
        
        if action == "list":
            await self.list_tasks()
        elif action == "create":
            await self.create_task_interactive()
        elif action == "kanban":
            await self.show_kanban()
        elif action == "complete":
            task_id = int(args[0]) if args else None
            if task_id:
                await self.complete_task(task_id)
        elif action == "delete":
            task_id = int(args[0]) if args else None
            if task_id:
                await self.delete_task(task_id)
        else:
            await self.interactive_menu()
    
    async def list_tasks(self, status: Optional[str] = None):
        """List all tasks"""
        with self.console.status("Loading tasks...", spinner="dots"):
            response = await self.client.list_tasks(status=status)
        
        if not response.success:
            self.console.print(f"[red]Error: {response.error}[/red]")
            return
        
        tasks = response.data.get("tasks", [])
        
        if not tasks:
            self.console.print("[dim]No tasks found[/dim]")
            return
        
        # Create table
        table = Table(title="Tasks", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Priority", style="red", width=10)
        table.add_column("Title", style="white")
        table.add_column("Created", style="dim", width=16)
        
        for task in tasks:
            status_emoji = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅",
                "failed": "❌"
            }.get(task.get("status", "pending"), "○")
            
            priority_style = {
                "low": "green",
                "medium": "yellow",
                "high": "red",
                "critical": "bold red"
            }.get(task.get("priority", "medium"), "white")
            
            table.add_row(
                str(task.get("id")),
                f"{status_emoji} {task.get('status', 'pending')}",
                f"[{priority_style}]{task.get('priority', 'medium')}[/{priority_style}]",
                task.get("title", "Untitled"),
                task.get("created_at", "")[:16] if task.get("created_at") else ""
            )
        
        self.console.print(table)
    
    async def show_kanban(self):
        """Show kanban board view"""
        with self.console.status("Loading tasks...", spinner="dots"):
            response = await self.client.list_tasks()
        
        if not response.success:
            self.console.print(f"[red]Error: {response.error}[/red]")
            return
        
        tasks = response.data.get("tasks", [])
        
        # Group tasks by status
        grouped = {
            "pending": [],
            "in_progress": [],
            "completed": []
        }
        
        for task in tasks:
            status = task.get("status", "pending")
            if status in grouped:
                grouped[status].append(task)
        
        # Create columns
        columns = []
        
        for status, status_tasks in grouped.items():
            status_display = status.replace("_", " ").title()
            
            # Create column panel
            task_items = []
            for task in status_tasks[:10]:  # Show top 10
                priority_marker = {
                    "low": "🟢",
                    "medium": "🟡",
                    "high": "🔴",
                    "critical": "🔥"
                }.get(task.get("priority", "medium"), "⚪")
                
                task_items.append(
                    f"{priority_marker} [{task.get('id')}] {task.get('title', 'Untitled')[:30]}"
                )
            
            if not task_items:
                task_items.append("[dim]No tasks[/dim]")
            
            column_content = "\n".join(task_items)
            
            # Color-code panels
            style = {
                "pending": "yellow",
                "in_progress": "cyan",
                "completed": "green"
            }.get(status, "white")
            
            panel = Panel(
                column_content,
                title=f"[bold]{status_display}[/bold] ({len(status_tasks)})",
                border_style=style,
                expand=True
            )
            columns.append(panel)
        
        self.console.print(Columns(columns, equal=True, expand=True))
    
    async def create_task_interactive(self):
        """Create task interactively"""
        self.console.print("\n[bold]Create New Task[/bold]")
        
        title = await asyncio.to_thread(Prompt.ask, "Task title")
        if not title:
            self.console.print("[yellow]Cancelled[/yellow]")
            return
        
        description = await asyncio.to_thread(Prompt.ask, "Description (optional)", default="")
        priority = await asyncio.to_thread(
            Prompt.ask,
            "Priority",
            choices=["low", "medium", "high", "critical"],
            default="medium"
        )
        
        with self.console.status("Creating task...", spinner="dots"):
            response = await self.client.create_task(
                title=title,
                description=description,
                priority=priority
            )
        
        if response.success:
            task = response.data.get("task", {})
            self.console.print(f"[green]✓ Task created: #{task.get('id')} - {title}[/green]")
        else:
            self.console.print(f"[red]Error: {response.error}[/red]")
    
    async def complete_task(self, task_id: int):
        """Mark task as completed"""
        with self.console.status(f"Completing task #{task_id}...", spinner="dots"):
            response = await self.client.complete_task(task_id)
        
        if response.success:
            self.console.print(f"[green]✓ Task #{task_id} completed[/green]")
        else:
            self.console.print(f"[red]Error: {response.error}[/red]")
    
    async def delete_task(self, task_id: int):
        """Delete a task"""
        confirm = await asyncio.to_thread(
            Confirm.ask,
            f"Delete task #{task_id}?"
        )
        
        if not confirm:
            self.console.print("[yellow]Cancelled[/yellow]")
            return
        
        with self.console.status(f"Deleting task #{task_id}...", spinner="dots"):
            response = await self.client.delete_task(task_id)
        
        if response.success:
            self.console.print(f"[green]✓ Task #{task_id} deleted[/green]")
        else:
            self.console.print(f"[red]Error: {response.error}[/red]")
    
    async def interactive_menu(self):
        """Interactive task management menu"""
        while True:
            self.console.clear()
            await self.show_kanban()
            
            self.console.print("\n[bold]Task Management[/bold]")
            self.console.print("1. List all tasks")
            self.console.print("2. Create new task")
            self.console.print("3. Complete task")
            self.console.print("4. Delete task")
            self.console.print("5. Refresh")
            self.console.print("0. Back to main menu")
            
            choice = await asyncio.to_thread(self.console.input, "\nChoice: ")
            
            if choice == "1":
                await self.list_tasks()
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
            elif choice == "2":
                await self.create_task_interactive()
            elif choice == "3":
                task_id = await asyncio.to_thread(self.console.input, "Task ID: ")
                if task_id.isdigit():
                    await self.complete_task(int(task_id))
            elif choice == "4":
                task_id = await asyncio.to_thread(self.console.input, "Task ID: ")
                if task_id.isdigit():
                    await self.delete_task(int(task_id))
            elif choice == "5":
                continue
            elif choice == "0":
                break
