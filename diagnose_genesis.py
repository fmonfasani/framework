#!/usr/bin/env python3
import sys
import os
from pathlib import Path

print("� Diagnóstico de Genesis Engine")
print("=" * 40)

# Verificar instalación
try:
    import genesis_engine
    print(f"✅ Genesis Engine v{genesis_engine.__version__} instalado")
except ImportError:
    print("❌ Genesis Engine no instalado")
    sys.exit(1)

# Verificar ruta de scripts
scripts_path = Path(sys.executable).parent / "Scripts"
user_scripts = Path.home() / "AppData/Roaming/Python/Python311/Scripts"

print(f"\n� Rutas importantes:")
print(f"Python executable: {sys.executable}")
print(f"Scripts path: {scripts_path}")
print(f"User scripts: {user_scripts}")

# Verificar genesis.exe
genesis_locations = [
    scripts_path / "genesis.exe",
    user_scripts / "genesis.exe",
    scripts_path / "genesis",
    user_scripts / "genesis"
]

print(f"\n� Buscando genesis:")
for location in genesis_locations:
    if location.exists():
        print(f"✅ Encontrado: {location}")
    else:
        print(f"❌ No existe: {location}")

# Verificar PATH
current_path = os.environ.get('PATH', '').split(os.pathsep)
print(f"\n�️ PATH actual contiene:")
for path in current_path:
    if 'Python' in path and 'Scripts' in path:
        print(f"✅ {path}")

# Comando sugerido
print(f"\n� Comandos para probar:")
print(f"python -m genesis_engine.cli.main --version")
print(f'export PATH="$PATH:{user_scripts.as_posix()}"')
