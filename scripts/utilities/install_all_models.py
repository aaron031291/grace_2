#!/usr/bin/env python3
"""
Install All Grace Models - Ollama Installer
Installs all 15 recommended open source models for Grace
"""

import subprocess
import sys
import requests
from typing import List, Dict

# All 15 Grace recommended models
GRACE_MODELS = {
    'qwen2.5:32b': 'Conversation & reasoning',
    'qwen2.5:72b': 'Ultimate quality',
    'deepseek-coder-v2:16b': 'Best coding',
    'deepseek-r1:70b': 'Complex reasoning (o1-level)',
    'kimi:latest': '128K context',
    'llava:34b': 'Vision + text',
    'com'
    'nd-r-plus:latest': 'RAG specialist',
    'phi3.5:latest': 'Ultra fast',
    'codegemma:7b': 'Code completion',
    'granite-code:20b': 'Enterprise code',
    'dolphin-mixtral:latest': 'Uncensored',
    'nous-hermes2-mixtral:latest': 'Instructions',
    'gemma2:9b': 'Fast general',
    'llama3.2:latest': 'Lightweight',
    'mistral-nemo:latest': 'Efficient'
}


def check_ollama_running() -> bool:
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_installed_models() -> List[str]:
    """Get list of currently installed models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models_data = response.json()
            return [m['name'] for m in models_data.get('models', [])]
    except:
        pass
    return []


def get_missing_models() -> List[str]:
    """Get list of models that need to be installed"""
    installed = get_installed_models()
    
    missing = []
    for model in GRACE_MODELS.keys():
        # Check if model base name is in installed
        model_base = model.split(':')[0]
        if not any(model_base in inst for inst in installed):
            missing.append(model)
    
    return missing


def install_model(model: str) -> bool:
    """Install a single model using ollama pull"""
    print(f"\n{'='*60}")
    print(f"Installing: {model}")
    print(f"Purpose: {GRACE_MODELS[model]}")
    print(f"{'='*60}")
    
    try:
        # Run ollama pull
        result = subprocess.run(
            ['ollama', 'pull', model],
            check=True,
            capture_output=False,
            text=True
        )
        
        print(f"[OK] Installed: {model}")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install {model}: {e}")
        return False
    
    except FileNotFoundError:
        print(f"[ERROR] Ollama command not found. Is Ollama installed?")
        print(f"   Install from: https://ollama.ai")
        return False


def main():
    """Main installation flow"""
    print("=" * 60)
    print("GRACE MODEL INSTALLER")
    print("=" * 60)
    print()
    
    # Check Ollama is running
    if not check_ollama_running():
        print("✗ Ollama is not running!")
        print()
        print("Start Ollama first:")
        print("  Windows: ollama serve")
        print("  macOS/Linux: ollama serve")
        print()
        sys.exit(1)
    
    print("[OK] Ollama is running")
    print()
    
    # Check what's installed
    installed = get_installed_models()
    missing = get_missing_models()
    
    print(f"Total Grace models: 15")
    print(f"Already installed: {15 - len(missing)}")
    print(f"Missing: {len(missing)}")
    print()
    
    if not missing:
        print("[OK] All Grace models are already installed!")
        print()
        print("Installed models:")
        for model in GRACE_MODELS.keys():
            print(f"  • {model} - {GRACE_MODELS[model]}")
        sys.exit(0)
    
    # Show what will be installed
    print("Models to install:")
    for model in missing:
        print(f"  • {model} - {GRACE_MODELS[model]}")
    print()
    
    # Ask for confirmation
    response = input("Install all missing models? (y/N): ").strip().lower()
    
    if response != 'y':
        print("Installation cancelled.")
        sys.exit(0)
    
    # Install each missing model
    print()
    print("Starting installation...")
    print()
    
    success_count = 0
    failed = []
    
    for i, model in enumerate(missing, 1):
        print(f"\n[{i}/{len(missing)}] Installing {model}...")
        
        if install_model(model):
            success_count += 1
        else:
            failed.append(model)
    
    # Summary
    print()
    print("=" * 60)
    print("INSTALLATION COMPLETE")
    print("=" * 60)
    print()
    print(f"Successful: {success_count}/{len(missing)}")
    
    if failed:
        print(f"Failed: {len(failed)}")
        print()
        print("Failed models:")
        for model in failed:
            print(f"  - {model}")
        print()
        print("Retry failed models manually:")
        for model in failed:
            print(f"  ollama pull {model}")
    else:
        print()
        print("[OK] All models installed successfully!")
    
    print()
    print("You can now restart Grace:")
    print("  python serve.py")
    print()


if __name__ == "__main__":
    main()
