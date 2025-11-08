from typing import Dict, Callable, Any
from dataclasses import dataclass
import importlib
import inspect

@dataclass
class Plugin:
    name: str
    version: str
    description: str
    author: str
    hooks: Dict[str, Callable]
    enabled: bool = True

class PluginManager:
    """Extensible plugin system for Grace"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, list] = {}
    
    def register_plugin(self, plugin: Plugin):
        """Register a new plugin"""
        self.plugins[plugin.name] = plugin
        
        for hook_name, hook_func in plugin.hooks.items():
            if hook_name not in self.hooks:
                self.hooks[hook_name] = []
            self.hooks[hook_name].append((plugin.name, hook_func))
        
        print(f"[OK] Plugin registered: {plugin.name} v{plugin.version}")
    
    async def execute_hook(self, hook_name: str, *args, **kwargs) -> list:
        """Execute all functions registered to a hook"""
        results = []
        
        if hook_name not in self.hooks:
            return results
        
        for plugin_name, hook_func in self.hooks[hook_name]:
            plugin = self.plugins.get(plugin_name)
            if not plugin or not plugin.enabled:
                continue
            
            try:
                if inspect.iscoroutinefunction(hook_func):
                    result = await hook_func(*args, **kwargs)
                else:
                    result = hook_func(*args, **kwargs)
                results.append((plugin_name, result))
            except Exception as e:
                print(f"[FAIL] Plugin {plugin_name} hook {hook_name} error: {e}")
        
        return results
    
    def list_plugins(self) -> list:
        """List all registered plugins"""
        return [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "author": p.author,
                "enabled": p.enabled,
                "hooks": list(p.hooks.keys())
            }
            for p in self.plugins.values()
        ]
    
    def enable_plugin(self, name: str):
        """Enable a plugin"""
        if name in self.plugins:
            self.plugins[name].enabled = True
            print(f"[OK] Plugin enabled: {name}")
    
    def disable_plugin(self, name: str):
        """Disable a plugin"""
        if name in self.plugins:
            self.plugins[name].enabled = False
            print(f"[OK] Plugin disabled: {name}")

plugin_manager = PluginManager()

# Example plugin
example_plugin = Plugin(
    name="example",
    version="1.0.0",
    description="Example plugin showing hook usage",
    author="Grace Team",
    hooks={
        "before_chat": lambda message: print(f"Plugin: Chat message received: {message[:20]}..."),
        "after_reflection": lambda reflection: print(f"Plugin: Reflection generated"),
    }
)

# Register example (commented out by default)
# plugin_manager.register_plugin(example_plugin)
