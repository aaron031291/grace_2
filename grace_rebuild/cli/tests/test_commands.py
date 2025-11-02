"""
Command tests
"""

import pytest
from unittest.mock import Mock, AsyncMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from grace_client import GraceAPIClient, GraceResponse
from commands.chat_command import ChatCommand
from commands.tasks_command import TasksCommand


@pytest.mark.asyncio
class TestChatCommand:
    """Test chat command"""
    
    async def test_send_message(self, mocker):
        """Test sending a chat message"""
        client = Mock(spec=GraceAPIClient)
        client.is_authenticated.return_value = True
        client.chat = AsyncMock(return_value=GraceResponse(
            success=True,
            data={"response": "Test response"}
        ))
        
        console = Console()
        chat_cmd = ChatCommand(client, console)
        
        await chat_cmd.send_message("Test message")
        
        # Verify chat was called
        client.chat.assert_called_once_with("Test message")
        
        # Verify history was updated
        assert len(chat_cmd.history) == 2
        assert chat_cmd.history[0]["role"] == "user"
        assert chat_cmd.history[1]["role"] == "assistant"


@pytest.mark.asyncio
class TestTasksCommand:
    """Test tasks command"""
    
    async def test_list_tasks(self, mocker):
        """Test listing tasks"""
        client = Mock(spec=GraceAPIClient)
        client.is_authenticated.return_value = True
        client.list_tasks = AsyncMock(return_value=GraceResponse(
            success=True,
            data={"tasks": [
                {"id": 1, "title": "Test task", "status": "pending"}
            ]}
        ))
        
        console = Console()
        tasks_cmd = TasksCommand(client, console)
        
        await tasks_cmd.list_tasks()
        
        client.list_tasks.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
