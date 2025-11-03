from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..plugin_system import plugin_manager

router = APIRouter(prefix="/api/plugins", tags=["plugins"])

@router.get("/")
async def list_plugins():
    """List all registered plugins"""
    return {"plugins": plugin_manager.list_plugins()}

@router.post("/{plugin_name}/enable")
async def enable_plugin(
    plugin_name: str,
    current_user: str = Depends(get_current_user)
):
    """Enable a plugin"""
    plugin_manager.enable_plugin(plugin_name)
    return {"status": "enabled", "plugin": plugin_name}

@router.post("/{plugin_name}/disable")
async def disable_plugin(
    plugin_name: str,
    current_user: str = Depends(get_current_user)
):
    """Disable a plugin"""
    plugin_manager.disable_plugin(plugin_name)
    return {"status": "disabled", "plugin": plugin_name}
