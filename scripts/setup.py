#!/usr/bin/env python3
"""
Setup script for DDD Claims Processing System

This script helps set up the environment, check dependencies,
and configure the system for local model usage.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_ollama_installed() -> bool:
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_ollama_running() -> bool:
    """Check if Ollama service is running"""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        return True
    except Exception:
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible"""
    version = sys.version_info
    return version.major == 3 and version.minor >= 10


def setup_env_file() -> None:
    """Create .env file from .env.example if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
        print("   Please update MODEL_PROVIDER and model settings in .env")
    else:
        print("⚠️  .env.example not found, creating basic .env file")
        env_file.write_text("""# Model Provider Configuration
MODEL_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
""")
        print("✅ Created basic .env file")


def install_dependencies(use_venv: bool = True) -> None:
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    # Check if venv exists
    venv_path = Path("venv")
    if use_venv and venv_path.exists():
        print("   Using virtual environment...")
        pip_cmd = str(venv_path / "bin" / "pip")
        python_cmd = str(venv_path / "bin" / "python")
    else:
        pip_cmd = f"{sys.executable} -m pip"
        python_cmd = sys.executable
    
    try:
        if use_venv and venv_path.exists():
            subprocess.run(
                [pip_cmd, "install", "-r", "requirements.txt"],
                check=True,
                cwd=Path(__file__).parent.parent
            )
        else:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
                cwd=Path(__file__).parent.parent
            )
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("   Try running: pip install -r requirements.txt")
        if not venv_path.exists() and use_venv:
            print("   Or create venv first: python3 -m venv venv")


def create_venv_if_needed() -> bool:
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("\n📦 Creating virtual environment...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", "venv"],
            check=True,
            cwd=Path(__file__).parent.parent
        )
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Failed to create virtual environment")
        print("   Continuing with system Python...")
        return False

def main():
    """Main setup function"""
    print("🚀 DDD Claims Processing System - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        print("❌ Python 3.10+ is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print("✅ Python version is compatible")
    
    # Create virtual environment
    venv_created = create_venv_if_needed()
    
    # Check Ollama
    if not check_ollama_installed():
        print("\n⚠️  Ollama is not installed")
        print("   Install it from: https://ollama.com")
        print("   Or run: brew install ollama (macOS)")
        print("   Note: Demo works without Ollama using mock mode")
    else:
        print("✅ Ollama is installed")
        
        if not check_ollama_running():
            print("\n⚠️  Ollama service is not running")
            print("   Start it with: ollama serve")
            print("   Or run: ./scripts/setup_ollama.sh")
            print("   Note: Demo works without Ollama using mock mode")
        else:
            print("✅ Ollama service is running")
    
    # Setup environment file
    print("\n📝 Setting up environment configuration...")
    setup_env_file()
    
    # Install dependencies
    install_dependencies(use_venv=venv_created)
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\n📋 Next steps:")
    if venv_created:
        print("  1. Activate virtual environment: source venv/bin/activate")
        print("  2. Run the application:")
        print("     - python demo.py (for interactive demo)")
        print("     - streamlit run streamlit_app.py (for web dashboard)")
    else:
        print("  1. Run the application:")
        print("     - python demo.py (for interactive demo)")
        print("     - streamlit run streamlit_app.py (for web dashboard)")
    print("\n💡 Optional:")
    print("  - Ensure Ollama is running: ollama serve")
    print("  - Download a model: ollama pull llama3.2")
    print("  - Update .env with your model preferences")
    print("\n💡 For more help, see README.md")


if __name__ == "__main__":
    main()

