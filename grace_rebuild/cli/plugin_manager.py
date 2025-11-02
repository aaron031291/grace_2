"""
Plugin system for Grace CLI
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from rich.console import Console


@dataclass
class PluginMetadata:
    """Plugin metadata"""
    name: str
    version: str
    author: str
    description: str
    commands: List[str]


class PluginHooks:
    """Plugin hook system"""
    
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register(self, hook_name: str, callback: Callable):
        """Register a hook callback"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    async def trigger(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger all callbacks for a hook"""
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        result = await callback(*args, **kwargs)
                    else:
                        result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    print(f"Error in hook {hook_name}: {e}")
        return results


class Plugin:
    """Base plugin class"""
    
    def __init__(self, console: Console, client):
        self.console = console
        self.client = client
        self.metadata = PluginMetadata(
            name="BasePlugin",
            version="1.0.0",
            author="Unknown",
            description="Base plugin",
            commands=[]
        )
    
    async def on_load(self):
        """Called when plugin is loaded"""
        pass
    
    async def on_unload(self):
        """Called when plugin is unloaded"""
        pass
    
    async def on_command(self, command: str, args: List[str]) -> bool:
        """Handle custom command. Return True if handled."""
        return False
    
    async def on_message(self, role: str, content: str):
        """Called on chat message"""
        pass
    
    async def on_event(self, event_type: str, data: Dict[str, Any]):
        """Called on system event"""
        pass


class PluginManager:
    """Manage CLI plugins"""
    
    def __init__(self, plugin_dir: Path, console: Console, client):
        self.plugin_dir = plugin_dir
        self.console = console
        self.client = client
        self.plugins: Dict[str, Plugin] = {}
        self.hooks = PluginHooks()
    
    def discover_plugins(self) -> List[Path]:
        """Discover available plugins"""
        plugins = []
        
        if not self.plugin_dir.exists():
            return plugins
        
        # Find .py files and packages
        for item in self.plugin_dir.iterdir():
            if item.is_file() and item.suffix == '.py' and not item.name.startswith('_'):
                plugins.append(item)
            elif item.is_dir() and (item / '__init__.py').exists():
                plugins.append(item / '__init__.py')
        
        return plugins
    
    async def load_plugin(self, plugin_path: Path) -> bool:
        """Load a single plugin"""
        try:
            # Load module
            spec = importlib.util.spec_from_file_location(
                plugin_path.stem,
                plugin_path
            )
            if not spec or not spec.loader:
                self.console.print(f"[red]Failed to load plugin: {plugin_path.name}[/red]")
                return False
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_path.stem] = module
            spec.loader.exec_module(module)
            
            # Find Plugin class
            plugin_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    issubclass(item, Plugin) and 
                    item is not Plugin):
                    plugin_class = item
                    break
            
            if not plugin_class:
                self.console.print(f"[yellow]No Plugin class found in {plugin_path.name}[/yellow]")
                return False
            
            # Instantiate plugin
            plugin = plugin_class(self.console, self.client)
            await plugin.on_load()
            
            self.plugins[plugin.metadata.name] = plugin
            
            self.console.print(f"[green]✓ Loaded plugin: {plugin.metadata.name} v{plugin.metadata.version}[/green]")
            return True
        
        except Exception as e:
            self.console.print(f"[red]Error loading plugin {plugin_path.name}: {e}[/red]")
            return False
    
    async def load_all(self):
        """Load all discovered plugins"""
        plugins = self.discover_plugins()
        
        if not plugins:
            return
        
        self.console.print(f"\n[cyan]Loading {len(plugins)} plugin(s)...[/cyan]")
        
        for plugin_path in plugins:
            await self.load_plugin(plugin_path)
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            await plugin.on_unload()
            del self.plugins[plugin_name]
            self.console.print(f"[green]✓ Unloaded plugin: {plugin_name}[/green]")
            return True
        return False
    
    async def handle_command(self, command: str, args: List[str]) -> bool:
        """Let plugins handle command. Returns True if handled."""
        for plugin in self.plugins.values():
            try:
                if await plugin.on_command(command, args):
                    return True
            except Exception as e:
                self.console.print(f"[red]Error in plugin {plugin.metadata.name}: {e}[/red]")
        return False
    
    async def on_message(self, role: str, content: str):
        """Notify plugins of chat message"""
        for plugin in self.plugins.values():
            try:
                await plugin.on_message(role, content)
            except Exception as e:
                self.console.print(f"[red]Error in plugin {plugin.metadata.name}: {e}[/red]")
    
    async def on_event(self, event_type: str, data: Dict[str, Any]):
        """Notify plugins of system event"""
        for plugin in self.plugins.values():
            try:
                await plugin.on_event(event_type, data)
            except Exception as e:
                self.console.print(f"[red]Error in plugin {plugin.metadata.name}: {e}[/red]")
    
    def list_plugins(self) -> List[PluginMetadata]:
        """List loaded plugins"""
        return [plugin.metadata for plugin in self.plugins.values()]


import asyncio
