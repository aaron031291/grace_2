from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..plugin_system import plugin_manager
from ..schemas_extended import PluginsListResponse, PluginActionResponse

router = APIRouter(prefix="/api/plugins", tags=["plugins"])

@router.get("/", response_model=PluginsListResponse)
async def list_plugins():
    """List all registered plugins"""
    plugins = plugin_manager.list_plugins()
    return PluginsListResponse(
        plugins=plugins,
        count=len(plugins),
        execution_trace=None,
        data_provenance=[]
    )

@router.post("/{plugin_name}/enable", response_model=PluginActionResponse)
async def enable_plugin(
    plugin_name: str,
    current_user: str = Depends(get_current_user)
):
    """Enable a plugin"""
    plugin_manager.enable_plugin(plugin_name)
    return PluginActionResponse(
        status="enabled",
        plugin=plugin_name,
        execution_trace=None,
        data_provenance=[]
    )

@router.post("/{plugin_name}/disable", response_model=PluginActionResponse)
async def disable_plugin(
    plugin_name: str,
    current_user: str = Depends(get_current_user)
):
    """Disable a plugin"""
    plugin_manager.disable_plugin(plugin_name)
    return PluginActionResponse(
        status="disabled",
        plugin=plugin_name,
        execution_trace=None,
        data_provenance=[]
    )
