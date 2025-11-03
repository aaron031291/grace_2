# Grace CLI - Terminal Interface

A powerful, full-featured command-line interface for Grace AI with complete backend integration, real-time updates, and extensibility through plugins.

## Features

- **🔐 Authentication** - Secure login with token-based auth
- **💬 Chat** - Interactive chat with Grace AI
- **📋 Task Management** - Kanban board view for tasks
- **📚 Knowledge Base** - Ingest URLs with trust scoring
- **🛡️ Security Dashboard** - Hunter alerts with severity filtering
- **⚖️ Governance** - Approval workflow management
- **🔍 Verification** - Audit log viewer with statistics
- **💻 File Explorer** - Browse files with syntax highlighting
- **🎤 Voice Interface** - Audio recording and text-to-speech
- **🔌 Plugin System** - Extend functionality with custom plugins
- **⚙️ Configuration** - Customizable settings and themes

## Installation

### Prerequisites

- Python 3.9+
- Grace backend running (default: http://localhost:8000)
- pip package manager

### Quick Install

```bash
cd grace_rebuild/cli
pip install -r requirements.txt
```

### Full Installation with Audio Support

```bash
cd grace_rebuild/cli
pip install -r requirements.txt

# Windows
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

## Quick Start

### 1. Start Grace Backend

```bash
cd grace_rebuild
python -m uvicorn backend.main:app --reload
```

### 2. Run CLI

```bash
cd grace_rebuild/cli
python enhanced_grace_cli.py
```

### 3. First Time Setup

1. Choose **Register** to create an account
2. Enter username and password
3. CLI will automatically connect to backend
4. You're ready to use Grace!

## Usage

### Main Menu

After login, you'll see the main menu:

```
Grace AI - Main Menu

 1. 💬 Chat with Grace
 2. 📋 Task Management
 3. 📚 Knowledge Base
 4. 🛡️ Security Alerts
 5. ⚖️ Governance
 6. 🔍 Verification Logs
 7. 💻 File Explorer
 8. 🎤 Voice Interface
 9. 🔌 Plugins
10. ⚙️ Settings
11. ❓ Help
12. 🚪 Exit
```

### Command Reference

#### Chat
- **Purpose**: Interactive conversation with Grace AI
- **Features**: 
  - Streaming responses
  - Markdown rendering
  - Chat history
  - Context-aware responses

```
Commands:
- Type message and press Enter
- 'history' - View chat history
- 'clear' - Clear screen
- 'exit' - Return to main menu
```

#### Task Management
- **Purpose**: Create and manage tasks
- **Features**:
  - Kanban board view
  - Priority levels (low, medium, high, critical)
  - Status tracking (pending, in-progress, completed)
  - Filtering and sorting

```
Actions:
- List all tasks
- Create new task
- Complete task
- Delete task
- Kanban view
```

#### Knowledge Base
- **Purpose**: Ingest and search knowledge
- **Features**:
  - URL ingestion
  - Trust score calculation
  - Semantic search
  - Content preview

```
Actions:
- Ingest URL
- Search knowledge
- List all items
```

#### Security Alerts (Hunter)
- **Purpose**: Monitor security events
- **Features**:
  - Severity filtering (critical, high, medium, low, info)
  - Alert acknowledgment
  - Dashboard with statistics
  - Real-time updates

```
Actions:
- View dashboard
- List alerts
- Filter by severity
- Acknowledge alert
```

#### Governance
- **Purpose**: Manage approval workflows
- **Features**:
  - Pending request notifications
  - Approve/reject with comments
  - Request history
  - Status tracking

```
Actions:
- List requests
- Approve request
- Reject request
- View details
```

#### Verification
- **Purpose**: View audit logs
- **Features**:
  - Audit log viewer
  - Statistics dashboard
  - Failed verification tracking
  - Custom time ranges

```
Actions:
- View audit log
- View statistics
- View failed verifications
- Filter by time range
```

#### File Explorer (IDE)
- **Purpose**: Browse and view files
- **Features**:
  - Directory tree view
  - Syntax highlighting (Python, JS, JSON, etc.)
  - File icons
  - Quick navigation

```
Actions:
- Open file
- Change directory
- Parent directory
- Refresh view
```

#### Voice Interface
- **Purpose**: Audio recording and TTS
- **Features**:
  - Microphone recording
  - Speech-to-text transcription
  - Text-to-speech synthesis
  - Audio playback

```
Actions:
- Record audio (5s, 10s, custom)
- Text to speech
- Auto-transcribe to chat
```

## Configuration

Configuration is stored in `~/.grace/config.yaml`

### Default Configuration

```yaml
backend_url: http://localhost:8000
theme: dark
auto_login: false
websocket_enabled: true
voice_enabled: true
plugins_enabled: true

# UI Settings
command_palette_key: ctrl+p
sidebar_width: 30
chat_history_limit: 50
task_refresh_interval: 5

# Audio Settings
audio_format: wav
sample_rate: 16000
channels: 1
```

### Modifying Settings

1. Go to Settings menu
2. Choose setting to change
3. Changes are saved immediately

Or edit `~/.grace/config.yaml` directly.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+C | Cancel current operation |
| Ctrl+P | Command palette (future) |
| Enter | Confirm/Submit |
| Esc | Cancel/Back |

## Plugin Development

### Creating a Plugin

1. Create `~/.grace/plugins/my_plugin.py`:

```python
from cli.plugin_manager import Plugin, PluginMetadata

class MyPlugin(Plugin):
    def __init__(self, console, client):
        super().__init__(console, client)
        self.metadata = PluginMetadata(
            name="MyPlugin",
            version="1.0.0",
            author="Your Name",
            description="My custom plugin",
            commands=["mycommand"]
        )
    
    async def on_load(self):
        self.console.print("[green]MyPlugin loaded![/green]")
    
    async def on_command(self, command: str, args: list) -> bool:
        if command == "mycommand":
            self.console.print("My custom command executed!")
            return True
        return False
    
    async def on_message(self, role: str, content: str):
        # Called on every chat message
        pass
    
    async def on_event(self, event_type: str, data: dict):
        # Called on system events
        pass
```

2. Restart CLI
3. Plugin will auto-load on startup

### Plugin Hooks

- `on_load()` - Called when plugin loads
- `on_unload()` - Called when plugin unloads
- `on_command(command, args)` - Handle custom commands
- `on_message(role, content)` - React to chat messages
- `on_event(event_type, data)` - React to system events

## Testing

### Run All Tests

```bash
cd grace_rebuild/cli
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_cli_basic.py -v
pytest tests/test_backend_integration.py -v
pytest tests/test_commands.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

## Troubleshooting

### Backend Connection Failed

```
Error: Backend not available: http://localhost:8000
```

**Solution**: Make sure Grace backend is running:
```bash
cd grace_rebuild
python -m uvicorn backend.main:app --reload
```

### Authentication Failed

```
Error: 401 Unauthorized
```

**Solution**: 
1. Clear stored credentials: Delete `~/.grace/config.yaml`
2. Re-login with correct credentials

### Audio Not Working

```
Error: PyAudio not installed
```

**Solution**: Install PyAudio dependencies:
```bash
# Windows
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

### Plugin Not Loading

**Check**:
1. Plugin file in `~/.grace/plugins/`
2. Plugin class inherits from `Plugin`
3. No syntax errors in plugin code
4. Plugins enabled in settings

## Directory Structure

```
cli/
├── commands/               # Command modules
│   ├── __init__.py
│   ├── chat_command.py
│   ├── tasks_command.py
│   ├── knowledge_command.py
│   ├── hunter_command.py
│   ├── governance_command.py
│   ├── verification_command.py
│   ├── ide_command.py
│   └── voice_command.py
├── tests/                  # Test files
│   ├── __init__.py
│   ├── test_cli_basic.py
│   ├── test_backend_integration.py
│   └── test_commands.py
├── grace_client.py         # API client
├── config.py               # Configuration management
├── plugin_manager.py       # Plugin system
├── voice_handler.py        # Audio handling
├── enhanced_grace_cli.py   # Main CLI application
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Advanced Usage

### Environment Variables

```bash
# Override backend URL
export GRACE_BACKEND_URL=http://custom:8000

# Disable plugins
export GRACE_PLUGINS_ENABLED=false
```

### Batch Mode

```bash
# Execute single command
python enhanced_grace_cli.py --command chat "Hello Grace"

# Execute multiple commands from file
python enhanced_grace_cli.py --batch commands.txt
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

- GitHub Issues: https://github.com/yourusername/grace/issues
- Documentation: https://grace-ai.readthedocs.io
- Discord: https://discord.gg/grace-ai

## Changelog

### v1.0.0 (2024-01-XX)
- Initial release
- Full backend integration
- 8 command modules
- Plugin system
- Voice interface
- Comprehensive testing
