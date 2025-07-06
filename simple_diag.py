import sys
import subprocess

print("=== DIAGNÓSTICO PYTHON ===")
print(f"Python actual: {sys.executable}")
print(f"Versión: {sys.version}")

# Verificar genesis-engine
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True)
    if "genesis-engine" in result.stdout:
        print("✅ Genesis Engine encontrado en este Python")
    else:
        print("❌ Genesis Engine NO encontrado en este Python")
        print("Lista de paquetes:")
        for line in result.stdout.split('\n'):
            if 'genesis' in line.lower():
                print(f"  {line}")
except Exception as e:
    print(f"Error: {e}")

# Verificar importación
try:
    import genesis_engine
    print(f"✅ genesis_engine importable: v{genesis_engine.__version__}")
except ImportError as e:
    print(f"❌ No se puede importar genesis_engine: {e}")
