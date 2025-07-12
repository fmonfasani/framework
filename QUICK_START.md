# 🚀 Genesis Engine - Guía de Inicio Rápido

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/genesis-engine/genesis-engine.git
cd genesis-engine

# Instalar Genesis Engine
pip install -e .  # incluye dependencias como PyYAML

# Verificar instalación
genesis --version
genesis doctor
```

## Crear tu primer proyecto

```bash
# Crear aplicación SaaS completa
genesis init mi-app --template=saas-basic

# Navegar al proyecto
cd mi-app

# Validar estructura
python ../validate_project.py .

# Ejecutar en desarrollo
docker-compose up -d
```

## Acceso a la aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

## Comandos útiles

```bash
# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Rebuild después de cambios
docker-compose up -d --build

# Limpiar volúmenes
docker-compose down -v
```

## Solución de problemas

### Error de Dockerfile faltante
```bash
# Regenerar proyecto
rm -rf mi-app
genesis init mi-app --template=saas-basic
```

### Error de encoding en Windows
```bash
# Verificar encoding
python apply_final_fixes.py
python verify_fixes.py
```

### Error de Pydantic
```bash
# Instalar dependencia faltante
pip install pydantic-settings
```

### Conflictos de Puertos

Al ejecutar `docker-compose up` cada servicio expone un puerto fijo en tu
máquina. Por ejemplo, Grafana usa el **3001** y Prometheus el **9090**. Si otro
proyecto ya está utilizando esos puertos obtendrás errores de arranque o los
dashboards no estarán disponibles.

**Opciones para resolverlo**:

1. Detén las instancias de otros proyectos con `docker-compose down` o
   `docker stop <id>` antes de iniciar uno nuevo.
2. Cambia los puertos editando tu `docker-compose.yml`. Modifica el valor a la
   izquierda del `:`. Ejemplo:

   ```yaml
   grafana:
     ports:
       - "3100:3000"  # host:contenedor
   prometheus:
     ports:
       - "9091:9090"
   ```

Luego ejecuta nuevamente `docker-compose up -d`.


## Estructura del proyecto

```
mi-app/
├── backend/           # FastAPI + SQLAlchemy
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/          # Next.js + TypeScript
│   ├── app/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml # Desarrollo local
├── monitoring/        # Prometheus + Grafana
└── .github/          # CI/CD GitHub Actions
```

## Próximos pasos

1. Personalizar entidades en `backend/app/models/`
2. Añadir componentes en `frontend/components/`
3. Configurar variables de entorno
4. Configurar despliegue en producción

## Soporte

- GitHub Issues: https://github.com/genesis-engine/genesis-engine/issues
- Documentación: docs/
- Discord: [Enlace a Discord]
