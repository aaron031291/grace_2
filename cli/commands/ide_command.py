"""
IDE command - File explorer and code viewer
"""

import asyncio
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree
from rich.prompt import Prompt
from ..grace_client import GraceAPIClient


class IDECommand:
    """File explorer and code viewer"""
    
    def __init__(self, client: GraceAPIClient, console: Console):
        self.client = client
        self.console = console
        self.current_dir = Path.cwd()
        self.current_file: Optional[Path] = None
    
    async def execute(self, path: Optional[str] = None):
        """Execute IDE command"""
        if path:
            self.current_dir = Path(path).absolute()
        
        await self.interactive_explorer()
    
    async def interactive_explorer(self):
        """Interactive file explorer"""
        while True:
            self.console.clear()
            
            # Show current directory tree
            self.show_directory_tree()
            
            self.console.print("\n[bold cyan]File Explorer[/bold cyan]")
            self.console.print(f"[dim]Current: {self.current_dir}[/dim]\n")
            
            self.console.print("1. Open file")
            self.console.print("2. Change directory")
            self.console.print("3. Parent directory")
            self.console.print("4. Refresh")
            self.console.print("0. Back to main menu")
            
            choice = await asyncio.to_thread(self.console.input, "\nChoice: ")
            
            if choice == "1":
                await self.open_file()
            elif choice == "2":
                await self.change_directory()
            elif choice == "3":
                self.current_dir = self.current_dir.parent
            elif choice == "4":
                continue
            elif choice == "0":
                break
    
    def show_directory_tree(self, max_depth: int = 2):
        """Show directory structure as tree"""
        tree = Tree(
            f"📁 [bold cyan]{self.current_dir.name}[/bold cyan]",
            guide_style="dim"
        )
        
        try:
            self._build_tree(tree, self.current_dir, current_depth=0, max_depth=max_depth)
            self.console.print(tree)
        except PermissionError:
            self.console.print("[red]Permission denied[/red]")
    
    def _build_tree(self, tree: Tree, directory: Path, current_depth: int, max_depth: int):
        """Recursively build directory tree"""
        if current_depth >= max_depth:
            return
        
        try:
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            
            # Limit items to prevent overflow
            if len(items) > 50:
                items = items[:50]
                tree.add("[dim]... (truncated)[/dim]")
            
            for item in items:
                # Skip hidden files
                if item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    branch = tree.add(f"📁 [cyan]{item.name}[/cyan]")
                    self._build_tree(branch, item, current_depth + 1, max_depth)
                else:
                    # File icon based on extension
                    icon = self._get_file_icon(item)
                    tree.add(f"{icon} [white]{item.name}[/white]")
        
        except PermissionError:
            tree.add("[red]Permission denied[/red]")
    
    def _get_file_icon(self, file: Path) -> str:
        """Get icon for file type"""
        ext = file.suffix.lower()
        
        icons = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.json': '📋',
            '.yaml': '📋',
            '.yml': '📋',
            '.md': '📝',
            '.txt': '📄',
            '.html': '🌐',
            '.css': '🎨',
            '.jpg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.pdf': '📕',
            '.zip': '📦',
        }
        
        return icons.get(ext, '📄')
    
    async def open_file(self):
        """Open and display a file"""
        filename = await asyncio.to_thread(
            self.console.input,
            "File name: "
        )
        
        if not filename:
            return
        
        file_path = self.current_dir / filename
        
        if not file_path.exists():
            self.console.print(f"[red]File not found: {filename}[/red]")
            await asyncio.sleep(1)
            return
        
        if file_path.is_dir():
            self.current_dir = file_path
            return
        
        self.current_file = file_path
        await self.view_file(file_path)
    
    async def view_file(self, file_path: Path):
        """View file with syntax highlighting"""
        self.console.clear()
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Limit file size for display
            if len(content) > 100000:
                self.console.print("[yellow]File too large to display (>100KB)[/yellow]")
                await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
                return
            
            # Determine language for syntax highlighting
            ext_to_lang = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.json': 'json',
                '.yaml': 'yaml',
                '.yml': 'yaml',
                '.md': 'markdown',
                '.html': 'html',
                '.css': 'css',
                '.sql': 'sql',
                '.sh': 'bash',
                '.bat': 'batch',
            }
            
            language = ext_to_lang.get(file_path.suffix.lower(), 'text')
            
            # Create syntax-highlighted view
            syntax = Syntax(
                content,
                language,
                theme="monokai",
                line_numbers=True,
                word_wrap=False
            )
            
            self.console.print(Panel(
                syntax,
                title=f"[bold]{file_path.name}[/bold]",
                subtitle=f"[dim]{file_path}[/dim]",
                border_style="cyan"
            ))
            
            await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
        
        except UnicodeDecodeError:
            self.console.print("[yellow]Binary file - cannot display[/yellow]")
            await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
        except Exception as e:
            self.console.print(f"[red]Error reading file: {e}[/red]")
            await asyncio.to_thread(self.console.input, "\nPress Enter to continue...")
    
    async def change_directory(self):
        """Change current directory"""
        new_dir = await asyncio.to_thread(
            self.console.input,
            "Directory path: "
        )
        
        if not new_dir:
            return
        
        dir_path = Path(new_dir)
        
        if not dir_path.is_absolute():
            dir_path = self.current_dir / dir_path
        
        if dir_path.exists() and dir_path.is_dir():
            self.current_dir = dir_path.absolute()
        else:
            self.console.print(f"[red]Directory not found: {new_dir}[/red]")
            await asyncio.sleep(1)
