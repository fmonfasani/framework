# 🚀 Genesis Engine

**Sistema operativo completo para desarrollo y despliegue de aplicaciones full-stack**

Genesis Engine es una plataforma innovadora que utiliza un equipo de agentes IA especializados para generar aplicaciones completas full-stack de manera automática. Desde el diseño de arquitectura hasta el despliegue en producción, Genesis Engine automatiza todo el pipeline de desarrollo.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Características Principales

### 🤖 Agentes IA Especializados

- **🏗️ ArchitectAgent**: Diseña arquitectura y entidades del proyecto
- **⚙️ BackendAgent**: Genera backend completo (FastAPI, Node/NestJS)
- **🎨 FrontendAgent**: Crea frontend moderno (React/Next.js, Vue)
- **🐳 DevOpsAgent**: Configura Docker, CI/CD y despliegue
- **🚀 DeployAgent**: Realiza despliegue automático
- **⚡ PerformanceAgent**: Optimiza rendimiento y seguridad
- **🧠 AIReadyAgent**: Prepara integración con IA y LLMs

### 🛠️ Stack Tecnológico Moderno

**Backend:**
- FastAPI (Python) + SQLAlchemy + PostgreSQL
- NestJS (TypeScript) + TypeORM + PostgreSQL
- Express.js + Prisma + MongoDB

**Frontend:**
- Next.js + TypeScript + Tailwind CSS + Redux Toolkit
- React + TypeScript + Styled Components + Zustand
- Vue 3 + TypeScript + Pinia + Vuetify

**DevOps:**
- Docker & Docker Compose
- GitHub Actions / GitLab CI
- Kubernetes manifests
- Nginx + SSL automático

### 🌟 Funcionalidades Avanzadas

- ✅ **Generación Completa**: Backend, frontend, DevOps y documentación
- ✅ **Despliegue Automático**: Local, cloud y containerizado
- ✅ **Golden Path**: Flujo optimizado para SaaS básico
- ✅ **Multi-Tenancy**: Soporte nativo para aplicaciones SaaS
- ✅ **Autenticación**: JWT, OAuth2, autenticación social
- ✅ **Billing**: Integración con Stripe para subscripciones
- ✅ **Monitoreo**: Prometheus, Grafana, logging estructurado
- ✅ **Testing**: Tests automatizados y CI/CD
- ✅ **Documentación**: API docs automática con OpenAPI/Swagger

## ⚠️ Estado Actual y Limitaciones

Genesis Engine aún está en una fase temprana de desarrollo. Algunas
funcionalidades se encuentran disponibles de forma **experimental** o todavía
no han sido implementadas por completo:

- `genesis deploy` — el comando ya ejecuta un despliegue local con
  Docker&nbsp;Compose si se ejecuta dentro de un proyecto válido. El soporte
  para otros targets (Docker standalone, Kubernetes y proveedores cloud como
  AWS, Heroku o Vercel) está incompleto y puede fallar.
- `genesis generate` — la generación de componentes individuales está en
  construcción.

Estas partes pueden cambiar sin previo aviso y es posible que presenten
comportamientos inesperados. Consulta la sección de [Roadmap](#-roadmap) para
conocer las características que llegarán próximamente.

## 🚀 Instalación Rápida

### Prerrequisitos

- Python 3.9+ 
- Node.js 18+
- Git
- Docker (opcional pero recomendado)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/genesis-engine/genesis-engine.git
cd genesis-engine

# Instalar Genesis Engine
pip install -e .

# Verificar instalación
genesis --version
genesis doctor
```

### Ensamblar desde Artefactos

Si sólo cuentas con los archivos de artefactos generados por los agentes,
puedes recrear la estructura del paquete ejecutando:

```bash
python assemble_genesis.py --artifacts path/to/artifacts
pip install -e .
```

El script copiará cada artefacto a su ubicación correspondiente y generará los
archivos `requirements.txt` y `pyproject.toml` necesarios.

### Verificación del Entorno

```bash
# Ejecutar diagnósticos completos
genesis doctor

# Resultado esperado:
# ✅ Python Version: Python 3.11.0 ✓
# ✅ Node.js Version: Node.js v18.17.0 ✓  
# ✅ Git Installation: git version 2.41.0 ✓
# ✅ Docker Installation: Docker version 24.0.5 ✓
# 🎉 Todas las verificaciones pasaron (8/8)
```

### Dependencias de desarrollo y pruebas

Para preparar un entorno de contribución instala las dependencias con los
extras de desarrollo y ejecuta la batería de tests:

```bash
pip install -e ".[dev]"
pytest
```

## 🎯 Uso Básico

### Mostrar Ayuda

```bash
genesis help
```

### Crear Proyecto con Golden Path (SaaS Básico)

```bash
# Crear aplicación SaaS completa
genesis init my-saas-app \
  --template=saas-basic

# Resultado:
# 🏗️ Analizando requisitos...
# 🎨 Diseñando arquitectura...
# ⚙️ Generando backend FastAPI...
# 🎨 Generando frontend Next.js...
# 🐳 Configurando DevOps...
# ✅ Proyecto 'my-saas-app' creado exitosamente!

cd my-saas-app
```

### Estructura Generada

```
my-saas-app/
├── backend/                 # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── routes/         # Endpoints API
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── services/       # Lógica de negocio
│   │   ├── auth/          # Autenticación JWT
│   │   └── db/            # Configuración DB
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic/           # Migraciones
├── frontend/               # Next.js + TypeScript
│   ├── app/               # App Router
│   ├── components/        # Componentes React
│   ├── lib/              # Utilities y API client
│   ├── store/            # Redux Toolkit
│   ├── types/            # Tipos TypeScript
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Desarrollo local
├── .github/workflows/      # CI/CD GitHub Actions
├── k8s/                   # Manifests Kubernetes
├── nginx/                 # Configuración Nginx
├── monitoring/            # Prometheus + Grafana
└── genesis.json           # Metadata del proyecto
```

### Ejecutar en Desarrollo

```bash
# Opción 1: Con Docker Compose (recomendado)
docker-compose up -d

# Opción 2: Manualmente
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm install
npm run dev

# Acceso:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## 🎨 Plantillas Disponibles

### Golden Path - SaaS Básico

Aplicación SaaS completa con todas las funcionalidades estándar:

- **Stack**: FastAPI + Next.js + PostgreSQL + Redis
- **Características**: Autenticación, billing, multi-tenancy, dashboard
- **Entidades**: User, Organization, Subscription, Invoice, Usage
- **Deployment**: Docker + GitHub Actions + Kubernetes

```bash
genesis init my-saas \
  --template=saas-basic \
  --features=authentication,billing,notifications
```

## 🛠️ Configuración Personalizada

### Stack Personalizado

El CLI actual no incluye una bandera para definir el stack. Para personalizar los
componentes del stack utiliza un archivo de configuración tal como se muestra en
la sección **Configuración Avanzada**.

### Características Específicas

```bash
genesis init my-app \
  --features=authentication \
  --features=file_upload \
  --features=search \
  --features=analytics \
  --features=admin_panel
```

### Configuración Avanzada

```bash
# Con archivo de configuración
cat > genesis.config.json << EOF
{
  "name": "advanced-app",
  "template": "custom",
  "stack": {
    "backend": "fastapi",
    "frontend": "nextjs", 
    "database": "postgresql",
    "cache": "redis",
    "search": "elasticsearch"
  },
  "features": [
    "authentication",
    "authorization", 
    "billing",
    "notifications",
    "file_upload",
    "search",
    "analytics"
  ],
  "deployment": {
    "platform": "kubernetes",
    "cloud": "aws",
    "monitoring": true,
    "ssl": true
  }
}
EOF

genesis create --config=genesis.config.json
```

## 🚀 Despliegue

### Despliegue Local

```bash
# Desarrollo con hot reload
genesis deploy --local --dev

# Producción local
genesis deploy --local --prod
```

### Despliegue en Cloud

```bash
# AWS
genesis deploy --cloud=aws --region=us-east-1

# Google Cloud
genesis deploy --cloud=gcp --region=us-central1

# Digital Ocean
genesis deploy --cloud=digitalocean --region=nyc1

# Heroku
genesis deploy --cloud=heroku
```

### Kubernetes

```bash
# Generar manifests
genesis generate k8s

# Aplicar a cluster
kubectl apply -f k8s/

# Con Helm
genesis deploy --k8s --helm
```

## 🤖 Arquitectura de Agentes

### Protocolo MCP (Multi-agent Communication Protocol)

Genesis Engine utiliza un protocolo personalizado para la comunicación entre agentes:

```python
# Ejemplo de comunicación entre agentes
async def architect_to_backend():
    # ArchitectAgent envía schema al BackendAgent
    response = await mcp.send_request(
        sender="architect_agent",
        recipient="backend_agent", 
        action="generate_backend",
        params={"schema": project_schema}
    )
    
    return response.result
```

### Flujo de Trabajo

```mermaid
graph TD
    A[Usuario ejecuta genesis init] --> B[ArchitectAgent]
    B --> C[Analiza requisitos]
    B --> D[Diseña arquitectura] 
    B --> E[Genera schema]
    E --> F[BackendAgent]
    E --> G[FrontendAgent]
    E --> H[DevOpsAgent]
    F --> I[Genera API + DB]
    G --> J[Genera UI + Estado]
    H --> K[Genera Docker + CI/CD]
    I --> L[DeployAgent]
    J --> L
    K --> L
    L --> M[Aplicación desplegada]
```

### Extensibilidad

Crear agentes personalizados:

```python
from genesis_engine.mcp.agent_base import GenesisAgent

class CustomAgent(GenesisAgent):
    def __init__(self):
        super().__init__(
            agent_id="custom_agent",
            name="CustomAgent",
            agent_type="custom"
        )
        
        self.add_capability("custom_generation")
        self.register_handler("custom_task", self._handle_custom_task)
    
    async def execute_task(self, task):
        # Lógica personalizada
        return result
```

## 📊 Monitoreo y Observabilidad

### Métricas Incluidas

- **Performance**: Response time, throughput, error rate
- **Business**: User registrations, subscriptions, revenue
- **Infrastructure**: CPU, memoria, disk, network
- **Application**: Logs estructurados, traces distribuidos

### Dashboards Grafana

- Application Overview
- API Performance  
- Database Metrics
- User Analytics
- Business KPIs

### Alertas Automáticas

- High error rate
- Slow response times
- Database connection issues
- Memory/CPU limits
- Failed deployments

## 🧪 Testing

### Tests Automáticos Incluidos

Las carpetas `backend/` y `frontend/` se crean solo después de ejecutar
`genesis init <nombre-del-proyecto>`. A continuación se muestra un flujo de
trabajo típico:

```bash
pip install -e .
genesis init my-app
cd my-app/backend && pytest
cd my-app/frontend && npm test
```

```bash
# Backend tests
cd backend && pytest

# Frontend tests  
cd frontend && npm test

# E2E tests
npm run test:e2e

# All tests
genesis test
```

Ejecuta `genesis test` siempre desde dentro del proyecto generado para que se
resuelvan correctamente las rutas y configuraciones.

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml (generado automáticamente)
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test Backend
        run: pytest backend/
      - name: Test Frontend
        run: npm test
      
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Production
        run: genesis deploy --cloud=aws
```

## 🎯 Casos de Uso

### SaaS B2B

```bash
genesis init my-b2b-saas \
  --template=saas-basic \
  --features=multi-tenancy,billing,sso,audit-logs
```

Características incluidas:
- Multi-tenancy completo
- Billing con Stripe
- SSO (SAML, OAuth)
- Audit logs
- Admin dashboard
- API REST completa

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key
STRIPE_SECRET_KEY=sk_test_...

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Customización de Templates

```python
# custom_template.py
from genesis_engine.templates.engine import TemplateEngine

# Registrar template personalizado
template_engine.register_template(
    name="my_custom_component",
    path="templates/custom/component.j2"
)

# Al renderizar se validará que todas las variables requeridas para
# cada plantilla estén presentes. Si falta alguna variable necesaria
# se lanzará una `ValueError`.
```

### Hooks y Extensiones

```python
# hooks.py
from genesis_engine.core.hooks import register_hook

@register_hook("after_backend_generation")
async def custom_post_processing(context):
    # Lógica personalizada después de generar backend
    pass
```

## 📚 Documentación

### Documentación Completa

- **[Guía de Instalación](docs/installation.md)**
- **[Tutorial Paso a Paso](docs/tutorial.md)**
- **[Referencia de API](docs/api-reference.md)**
- **[Arquitectura de Agentes](docs/agents.md)**
- **[Protocolo MCP](docs/mcp-protocol.md)**
- **[Templates y Plantillas](docs/templates.md)**
- **[Despliegue en Producción](docs/deployment.md)**
- **[Guía de Contribución](CONTRIBUTING.md)**

### Ejemplos

En el directorio `/examples` se incluye un script de demostración que muestra cómo
utilizar Genesis Engine de forma programática:

- [demo_complete.py](examples/demo_complete.py)

## 🤝 Contribuir

Genesis Engine es un proyecto open source. ¡Las contribuciones son bienvenidas!

### Desarrollo Local

```bash
# Clonar repo
git clone https://github.com/genesis-engine/genesis-engine.git
cd genesis-engine

# Setup desarrollo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Ejecutar tests
pytest

# Linting
black .
isort .
mypy .
```

### Crear un Agente

```python
# my_custom_agent.py
from genesis_engine.mcp.agent_base import GenesisAgent

class MyCustomAgent(GenesisAgent):
    def __init__(self):
        super().__init__(
            agent_id="my_custom_agent",
            name="MyCustomAgent", 
            agent_type="custom"
        )
        
        self.add_capability("custom_feature")
    
    async def execute_task(self, task):
        # Tu lógica aquí
        return result
```

## 🛣️ Roadmap

### v1.1 (Q3 2025)
- [ ] Soporte para más frameworks (Django, Spring Boot)
- [ ] Integración con más clouds (Azure, Vercel)
- [ ] Templates para Microservices
- [ ] AI-powered code optimization

### v1.2 (Q3 2025)
- [ ] Genesis Cloud (hosting gestionado)
- [ ] Marketplace de templates y agentes
- [ ] Preview deployments automáticos
- [ ] Monitoring avanzado con IA

### v2.0 (Q4 2025)
- [ ] Visual project builder
- [ ] Real-time collaboration
- [ ] Advanced AI agents (code review, optimization)
- [ ] Enterprise features

## 🐛 Issues y Soporte

### Reportar Bugs

- **[GitHub Issues](https://github.com/genesis-engine/genesis-engine/issues)**
- **[Discussions](https://github.com/genesis-engine/genesis-engine/discussions)**

### Soporte de la Comunidad

- **[Discord](https://discord.gg/genesis-engine)**
- **[Stack Overflow](https://stackoverflow.com/questions/tagged/genesis-engine)**

### Soporte Enterprise

Para organizaciones que necesitan soporte dedicado:
- **Email**: enterprise@genesis-engine.dev
- **Features**: SLA garantizado, templates personalizados, integración dedicada

## 📄 Licencia

Genesis Engine está licenciado bajo la [Licencia MIT](LICENSE).

## 🙏 Agradecimientos

Genesis Engine está construido sobre tecnologías open source increíbles:

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno para Python
- [Next.js](https://nextjs.org/) - Framework React para producción
- [Typer](https://typer.tiangolo.com/) - CLI moderna para Python
- [Rich](https://rich.readthedocs.io/) - Rich text y beautiful formatting
- [Jinja2](https://jinja.palletsprojects.com/) - Motor de templates
- [Docker](https://docker.com/) - Containerización
- [Kubernetes](https://kubernetes.io/) - Orquestación de contenedores

---

<div align="center">

**[🏠 Página Principal](https://genesis-engine.dev)** •
**[📖 Documentación](https://docs.genesis-engine.dev)** •
**[🚀 Demo en Vivo](https://demo.genesis-engine.dev)**

Creado con ❤️ por el equipo de Genesis Engine

</div>
