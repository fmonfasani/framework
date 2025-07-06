#!/usr/bin/env python3
import sys
import os
from pathlib import Path

print("Ì¥ç Diagn√≥stico de Genesis Engine")
print("=" * 40)

# Verificar instalaci√≥n
try:
    import genesis_engine
    print(f"‚úÖ Genesis Engine v{genesis_engine.__version__} instalado")
except ImportError:
    print("‚ùå Genesis Engine no instalado")
    sys.exit(1)

# Verificar ruta de scripts
scripts_path = Path(sys.executable).parent / "Scripts"
user_scripts = Path.home() / "AppData/Roaming/Python/Python311/Scripts"

print(f"\nÌ≥Å Rutas importantes:")
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

print(f"\nÌ¥ç Buscando genesis:")
for location in genesis_locations:
    if location.exists():
        print(f"‚úÖ Encontrado: {location}")
    else:
        print(f"‚ùå No existe: {location}")

# Verificar PATH
current_path = os.environ.get('PATH', '').split(os.pathsep)
print(f"\nÌª§Ô∏è PATH actual contiene:")
for path in current_path:
    if 'Python' in path and 'Scripts' in path:
        print(f"‚úÖ {path}")

# Comando sugerido
print(f"\nÌ≤° Comandos para probar:")
print(f"python -m genesis_engine.cli.main --version")
print(f'export PATH="$PATH:{user_scripts.as_posix()}"')
