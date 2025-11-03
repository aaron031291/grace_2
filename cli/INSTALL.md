# Grace CLI Installation Guide

Complete installation instructions for Grace CLI.

## Prerequisites

- **Python 3.9 or higher**
- **pip package manager**
- **Grace backend** (running at http://localhost:8000)
- **Git** (optional, for cloning repository)

## Installation Methods

### Method 1: Pip Install (Recommended)

```bash
# From the CLI directory
cd grace_rebuild/cli
pip install -e .

# Install with audio support
pip install -e ".[audio]"

# Install with development tools
pip install -e ".[dev]"
```

After installation, run:
```bash
grace
```

### Method 2: Direct Execution

```bash
cd grace_rebuild/cli
pip install -r requirements.txt
python enhanced_grace_cli.py
```

### Method 3: Windows Batch File

```bash
cd grace_rebuild\cli
grace.bat
```

## Platform-Specific Setup

### Windows

1. **Install Python 3.9+**
   - Download from https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

2. **Install Dependencies**
   ```cmd
   cd grace_rebuild\cli
   pip install -r requirements.txt
   ```

3. **Audio Support (Optional)**
   ```cmd
   pip install pyaudio
   ```
   
   If PyAudio installation fails, download pre-built wheel from:
   https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

4. **Run CLI**
   ```cmd
   python enhanced_grace_cli.py
   ```

### Linux (Ubuntu/Debian)

1. **Install Python and dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip portaudio19-dev
   ```

2. **Install CLI**
   ```bash
   cd grace_rebuild/cli
   pip3 install -r requirements.txt
   ```

3. **Audio Support**
   ```bash
   pip3 install pyaudio pydub
   ```

4. **Make script executable (optional)**
   ```bash
   chmod +x grace
   ./grace
   ```

### macOS

1. **Install Homebrew** (if not already installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python and PortAudio**
   ```bash
   brew install python portaudio
   ```

3. **Install CLI**
   ```bash
   cd grace_rebuild/cli
   pip3 install -r requirements.txt
   ```

4. **Audio Support**
   ```bash
   pip3 install pyaudio pydub
   ```

5. **Run CLI**
   ```bash
   python3 enhanced_grace_cli.py
   ```

## Post-Installation Setup

### 1. Start Grace Backend

Before using the CLI, ensure the backend is running:

```bash
cd grace_rebuild
python -m uvicorn backend.main:app --reload
```

Verify backend is running by visiting: http://localhost:8000/health

### 2. First Run

On first run, the CLI will:
1. Create config directory: `~/.grace/`
2. Create default config: `~/.grace/config.yaml`
3. Prompt for login/registration

### 3. Create User Account

Choose "Register" and enter:
- Username (alphanumeric)
- Password (minimum 8 characters recommended)

Your credentials are stored securely in the system keyring.

### 4. Verify Installation

Test all features:
```bash
# Chat
Type: chat
Message: "Hello Grace"

# Tasks
Type: tasks
Create a test task

# Knowledge
Type: knowledge
Search for something
```

## Configuration

Default configuration is created at `~/.grace/config.yaml`:

```yaml
backend_url: http://localhost:8000
theme: dark
auto_login: false
websocket_enabled: true
voice_enabled: true
plugins_enabled: true
```

Edit this file to customize settings.

## Troubleshooting

### Issue: "Module not found"

**Solution**:
```bash
# Ensure you're in the CLI directory
cd grace_rebuild/cli

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "Backend not available"

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, start it
cd grace_rebuild
python -m uvicorn backend.main:app --reload
```

### Issue: "PyAudio import error" (Windows)

**Solution**:
1. Download PyAudio wheel for your Python version
2. Install manually:
   ```cmd
   pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
   ```

### Issue: "Permission denied" (Linux/macOS)

**Solution**:
```bash
# Install with user flag
pip install -r requirements.txt --user

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Keyring backend error"

**Solution**:
```bash
# Use file-based keyring
pip install keyrings.alt

# Or disable auto-login in config
# Edit ~/.grace/config.yaml
auto_login: false
```

## Virtual Environment (Recommended)

Using a virtual environment prevents dependency conflicts:

```bash
# Create virtual environment
cd grace_rebuild/cli
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run CLI
python enhanced_grace_cli.py

# Deactivate when done
deactivate
```

## Docker Installation (Alternative)

Run CLI in Docker container:

```bash
# Build image
cd grace_rebuild/cli
docker build -t grace-cli .

# Run container
docker run -it --rm --network host grace-cli
```

## Updating

To update to the latest version:

```bash
cd grace_rebuild
git pull origin main

cd cli
pip install -r requirements.txt --upgrade
```

## Uninstallation

```bash
# If installed with pip
pip uninstall grace-cli

# Remove config directory
rm -rf ~/.grace

# Remove virtual environment (if used)
rm -rf venv
```

## Getting Help

- **Documentation**: See [README.md](README.md)
- **Issues**: Report bugs on GitHub
- **Support**: Join Discord community

## Next Steps

After installation:

1. **Read the README** - [README.md](README.md)
2. **Try the tutorial** - Type `help` in the CLI
3. **Explore plugins** - Check `~/.grace/plugins/`
4. **Customize settings** - Edit `~/.grace/config.yaml`

Happy coding with Grace! 🚀
