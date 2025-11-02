"""
Configuration for multi-language code execution engine
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class LanguageConfig:
    """Configuration for a specific language runtime"""
    name: str
    command: str
    compile_command: Optional[str] = None
    file_extension: str = ""
    timeout: int = 30
    memory_limit_mb: int = 512
    max_output_size: int = 100000
    requires_compilation: bool = False
    allow_network: bool = False
    env_vars: Dict[str, str] = None
    
    def __post_init__(self):
        if self.env_vars is None:
            self.env_vars = {}


LANGUAGE_CONFIGS: Dict[str, LanguageConfig] = {
    "python": LanguageConfig(
        name="Python",
        command="python",
        file_extension=".py",
        timeout=30,
        memory_limit_mb=512,
        env_vars={
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1"
        }
    ),
    "javascript": LanguageConfig(
        name="JavaScript (Node.js)",
        command="node --max-old-space-size=512",
        file_extension=".js",
        timeout=30,
        memory_limit_mb=512,
        env_vars={
            "NODE_ENV": "sandbox"
        }
    ),
    "typescript": LanguageConfig(
        name="TypeScript",
        command="node",
        compile_command="tsc --target ES2020 --module commonjs --outDir {output_dir}",
        file_extension=".ts",
        timeout=45,
        memory_limit_mb=512,
        requires_compilation=True,
        env_vars={
            "NODE_ENV": "sandbox"
        }
    ),
    "bash": LanguageConfig(
        name="Bash/Shell",
        command="bash",
        file_extension=".sh",
        timeout=20,
        memory_limit_mb=256,
    ),
    "sql": LanguageConfig(
        name="SQLite",
        command="sqlite3",
        file_extension=".sql",
        timeout=15,
        memory_limit_mb=256,
    ),
    "go": LanguageConfig(
        name="Go",
        command="go run",
        file_extension=".go",
        timeout=45,
        memory_limit_mb=1024,
        env_vars={
            "GOPATH": "{temp_dir}/go",
            "GOCACHE": "{temp_dir}/go-cache"
        }
    ),
    "rust": LanguageConfig(
        name="Rust",
        command="cargo run --manifest-path",
        compile_command="cargo build --manifest-path",
        file_extension=".rs",
        timeout=60,
        memory_limit_mb=1024,
        requires_compilation=True,
        env_vars={
            "CARGO_HOME": "{temp_dir}/cargo",
            "CARGO_TARGET_DIR": "{temp_dir}/target"
        }
    ),
}

SHELL_WHITELIST = {
    "echo", "cat", "ls", "pwd", "date", "whoami", "head", "tail",
    "grep", "find", "wc", "sort", "uniq", "tr", "cut", "sed", "awk",
    "mkdir", "touch", "cp", "mv", "rm"
}

SHELL_BLACKLIST = {
    "curl", "wget", "nc", "netcat", "telnet", "ssh", "scp", "ftp",
    "dd", "mkfs", "fdisk", "mount", "umount", "shutdown", "reboot",
    "systemctl", "service", "kill", "pkill", "sudo", "su",
    "chmod", "chown", "chgrp", "passwd"
}

@dataclass
class ExecutionPreset:
    """Execution mode presets"""
    name: str
    timeout_multiplier: float = 1.0
    memory_multiplier: float = 1.0
    allow_network: bool = False
    enable_logging: bool = True
    strict_limits: bool = False

EXECUTION_PRESETS: Dict[str, ExecutionPreset] = {
    "safe": ExecutionPreset(
        name="Safe Mode",
        timeout_multiplier=0.5,
        memory_multiplier=0.5,
        allow_network=False,
        enable_logging=True,
        strict_limits=True
    ),
    "dev": ExecutionPreset(
        name="Development Mode",
        timeout_multiplier=2.0,
        memory_multiplier=1.5,
        allow_network=True,
        enable_logging=True,
        strict_limits=False
    ),
    "production": ExecutionPreset(
        name="Production Mode",
        timeout_multiplier=1.0,
        memory_multiplier=1.0,
        allow_network=False,
        enable_logging=True,
        strict_limits=True
    ),
}

def get_language_config(language: str) -> LanguageConfig:
    """Get configuration for a language"""
    lang_key = language.lower()
    if lang_key not in LANGUAGE_CONFIGS:
        raise ValueError(f"Unsupported language: {language}")
    return LANGUAGE_CONFIGS[lang_key]

def get_execution_preset(preset: str = "dev") -> ExecutionPreset:
    """Get execution preset configuration"""
    preset_key = preset.lower()
    if preset_key not in EXECUTION_PRESETS:
        raise ValueError(f"Unknown preset: {preset}")
    return EXECUTION_PRESETS[preset_key]

def apply_preset_to_config(config: LanguageConfig, preset: ExecutionPreset) -> LanguageConfig:
    """Apply execution preset to language config"""
    config.timeout = int(config.timeout * preset.timeout_multiplier)
    config.memory_limit_mb = int(config.memory_limit_mb * preset.memory_multiplier)
    config.allow_network = preset.allow_network
    return config
