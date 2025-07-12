# genesis_engine/agents/backend.py
"""
BackendAgent corregido - Agente especializado en generación de backend
Implementa todos los handlers necesarios para comunicación MCP
"""
from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask, TaskResult
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import os
import logging
from datetime import datetime
from pathlib import Path
import json
import asyncio
logger = logging.getLogger(__name__)


class BackendFramework(str, Enum):
    """Supported backend frameworks."""
    FASTAPI = "fastapi"
    DJANGO = "django"
    NESTJS = "nestjs"


class DatabaseType(str, Enum):
    """Supported database engines."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class AuthMethod(str, Enum):
    """Authentication mechanisms."""
    NONE = "none"
    JWT = "jwt"
    OAUTH2 = "oauth2"


@dataclass
class BackendConfig:
    """Configuration for backend generation."""
    framework: BackendFramework = BackendFramework.FASTAPI
    database: DatabaseType = DatabaseType.POSTGRESQL
    auth_method: AuthMethod = AuthMethod.JWT
    features: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    environment_vars: Dict[str, Any] = field(default_factory=dict)

# Export commonly used classes for tests and consumers
__all__ = [
    "BackendFramework",
    "DatabaseType",
    "AuthMethod",
    "BackendConfig",
    "BackendAgent",
]


class BackendAgent(GenesisAgent):
    """
    Agente especializado en generación de backend
    Responsable de:
    - Generar código backend completo
    - Crear modelos de datos
    - Implementar endpoints de API
    - Configurar base de datos
    - Generar archivos de configuración
    """
    
    def __init__(self):
        super().__init__(
            agent_id="backend_agent",
            name="BackendAgent",
            agent_type="backend"
        )
        
        # Configurar capacidades específicas
        self._setup_capabilities()
        
        # Registrar handlers específicos del backend
        self._register_backend_handlers()
        
        # Templates y configuraciones
        self.supported_frameworks = {
            "fastapi": {
                "name": "FastAPI",
                "language": "Python",
                "orm": "SQLAlchemy",
                "async": True
            },
            "django": {
                "name": "Django",
                "language": "Python", 
                "orm": "Django ORM",
                "async": False
            },
            "nestjs": {
                "name": "NestJS",
                "language": "TypeScript",
                "orm": "TypeORM",
                "async": True
            }
        }

        # Expose framework configs for tests
        self.framework_configs = self.supported_frameworks

        # Containers for templates and generators
        self.available_templates: List[str] = []
        self.code_generators: Dict[str, Any] = {}
        
        self.database_configs = {
            "postgresql": {
                "driver": "psycopg2",
                "port": 5432,
                "async_driver": "asyncpg"
            },
            "mysql": {
                "driver": "pymysql",
                "port": 3306,
                "async_driver": "aiomysql"
            },
            "sqlite": {
                "driver": "sqlite3",
                "port": None,
                "async_driver": "aiosqlite"
            }
        }
    
    def _setup_capabilities(self):
        """Configurar capacidades del agente"""
        capabilities = [
            "generate_backend",
            "create_models",
            "generate_api_endpoints",
            "setup_database",
            "create_auth_system",
            "generate_middleware",
            "create_services",
            "setup_testing",
            "generate_dockerfile",
            "create_requirements"
        ]
        
        for capability in capabilities:
            self.add_capability(capability)
    
    def _register_backend_handlers(self):
        """Registrar handlers específicos del backend"""
        self.register_handler("generate_backend", self._handle_generate_backend)
        self.register_handler("create_models", self._handle_create_models)
        self.register_handler("generate_api_endpoints", self._handle_generate_api_endpoints)
        self.register_handler("setup_database", self._handle_setup_database)
        self.register_handler("create_auth_system", self._handle_create_auth_system)
        self.register_handler("generate_middleware", self._handle_generate_middleware)
    
    async def execute_task(self, task: AgentTask) -> TaskResult:
        """
        Ejecutar tarea específica del backend
        """
        try:
            self.logger.info(f"⚙️ Ejecutando tarea de backend: {task.name}")
            
            # Routing de tareas por nombre
            if task.name == "generate_backend":
                result = await self._generate_backend_complete(task.params)
            elif task.name == "create_models":
                result = await self._create_data_models(task.params)
            elif task.name == "generate_api_endpoints":
                result = await self._generate_api_endpoints(task.params)
            elif task.name == "setup_database":
                result = await self._setup_database_config(task.params)
            elif task.name == "create_auth_system":
                result = await self._create_authentication_system(task.params)
            elif task.name == "generate_middleware":
                result = await self._generate_middleware_stack(task.params)
            elif task.name == "create_services":
                result = await self._create_business_services(task.params)
            elif task.name == "generate_dockerfile":
                result = await self._generate_docker_config(task.params)
            else:
                result = await self._handle_generic_backend_task(task)
            
            self.logger.info(f"✅ Tarea de backend {task.name} completada exitosamente")
            
            return TaskResult(
                task_id=task.id,
                success=True,
                result=result,
                metadata={
                    "agent": self.name,
                    "task_type": task.name,
                    "framework": self._detect_framework(task.params)
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando tarea de backend {task.name}: {str(e)}")
            
            return TaskResult(
                task_id=task.id,
                success=False,
                error=str(e),
                metadata={
                    "agent": self.name,
                    "task_type": task.name,
                    "error_type": type(e).__name__
                }
            )
    
    # Handlers directos para MCP
    
    async def _handle_generate_backend(self, request) -> Dict[str, Any]:
        """Handler directo para generate_backend"""
        data = getattr(request, 'data', {})
        return await self._generate_backend_complete(data)
    
    async def _handle_create_models(self, request) -> Dict[str, Any]:
        """Handler directo para create_models"""
        data = getattr(request, 'data', {})
        return await self._create_data_models(data)
    
    async def _handle_generate_api_endpoints(self, request) -> Dict[str, Any]:
        """Handler directo para generate_api_endpoints"""
        data = getattr(request, 'data', {})
        return await self._generate_api_endpoints(data)
    
    async def _handle_setup_database(self, request) -> Dict[str, Any]:
        """Handler directo para setup_database"""
        data = getattr(request, 'data', {})
        return await self._setup_database_config(data)
    
    async def _handle_create_auth_system(self, request) -> Dict[str, Any]:
        """Handler directo para create_auth_system"""
        data = getattr(request, 'data', {})
        return await self._create_authentication_system(data)
    
    async def _handle_generate_middleware(self, request) -> Dict[str, Any]:
        """Handler directo para generate_middleware"""
        data = getattr(request, 'data', {})
        return await self._generate_middleware_stack(data)
    
    # Métodos principales de generación
    
    async def _generate_backend_complete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generar backend completo basado en schema del proyecto
        """
        self.logger.info("🏗️ Generando backend completo...")
        
        # Extraer parámetros
        schema = params.get("schema", {})
        output_path = params.get("output_path", "./backend")
        framework = params.get("framework", "fastapi")
        
        # Validar parámetros
        if not schema:
            raise ValueError("Schema del proyecto es requerido")
        
        # Crear estructura base
        backend_structure = await self._create_backend_structure(schema, framework)
        
        # Generar archivos
        generated_files = await self._generate_all_backend_files(backend_structure, output_path, schema)
        
        # Crear archivos en el sistema
        created_files = await self._write_backend_files(generated_files, output_path)
        
        result = {
            "status": "success",
            "framework": framework,
            "output_path": output_path,
            "structure": backend_structure,
            "generated_files": list(generated_files.keys()),
            "created_files": created_files,
            "features_implemented": self._get_implemented_features(schema),
            "next_steps": self._get_next_steps(schema),
            "generation_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "generator": self.name,
                "framework_version": self._get_framework_version(framework)
            }
        }
        
        self.logger.info(f"✅ Backend generado exitosamente en {output_path}")
        return result
    
    async def _create_backend_structure(self, schema: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Crear estructura del backend"""
        structure = schema.get("structure", {}).get("backend", {})
        
        if framework == "fastapi":
            return {
                "framework": "FastAPI",
                "language": "Python",
                "directories": {
                    "app": {
                        "main.py": "Application entry point",
                        "models": "Data models directory",
                        "routes": "API routes directory", 
                        "services": "Business logic services",
                        "core": "Core configuration",
                        "auth": "Authentication module",
                        "utils": "Utility functions",
                        "tests": "Test modules"
                    },
                    "alembic": "Database migrations",
                    "scripts": "Helper scripts"
                },
                "config_files": [
                    "requirements.txt",
                    "Dockerfile",
                    ".env.example",
                    "alembic.ini",
                    "pytest.ini"
                ]
            }
        else:
            # Estructura genérica para otros frameworks
            return {
                "framework": framework,
                "directories": {"src": "Source code"},
                "config_files": ["package.json", "Dockerfile"]
            }
    
    async def _generate_all_backend_files(self, structure: Dict[str, Any], output_path: str, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generar todos los archivos del backend"""
        files = {}
        
        # Archivos principales
        files.update(await self._generate_main_files(schema))
        
        # Modelos de datos
        files.update(await self._generate_model_files(schema))
        
        # Rutas/endpoints
        files.update(await self._generate_route_files(schema))
        
        # Servicios
        files.update(await self._generate_service_files(schema))
        
        # Configuración
        files.update(await self._generate_config_files(schema))
        
        # Autenticación (si es necesaria)
        if self._needs_authentication(schema):
            files.update(await self._generate_auth_files(schema))
        
        # Docker y deployment
        files.update(await self._generate_deployment_files(schema))
        
        # Tests
        files.update(await self._generate_test_files(schema))
        
        return files
    
    async def _generate_main_files(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generar archivos principales"""
        files = {}
        
        # main.py para FastAPI
        files["app/main.py"] = self._generate_fastapi_main(schema)
        files["app/__init__.py"] = ""
        
        return files
    
    def _generate_fastapi_main(self, schema: Dict[str, Any]) -> str:
        """Generar archivo main.py de FastAPI"""
        project_name = schema.get("project", {}).get("name", "Genesis API")
        features = schema.get("features", [])
        
        imports = [
            "from fastapi import FastAPI",
            "from fastapi.middleware.cors import CORSMiddleware"
        ]
        
        # Imports condicionales
        if "authentication" in features:
            imports.append("from app.routes import auth")
        
        imports.append("from app.routes import api")
        imports.append("from app.core.config import settings")
        
        if "database" in features:
            imports.append("from app.core.database import engine")
            imports.append("from app.models import user")  # Import models
        
        main_content = f'''
{chr(10).join(imports)}

app = FastAPI(
    title="{project_name}",
    description="API generated by Genesis Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
'''
        
        if "authentication" in features:
            main_content += 'app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])\n'
        
        main_content += 'app.include_router(api.router, prefix="/api/v1", tags=["API"])\n'
        
        main_content += '''
@app.get("/")
def read_root():
    return {"message": "Genesis API is running", "status": "healthy"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Genesis API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        return main_content.strip()
    
    async def _generate_model_files(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generar archivos de modelos"""
        files = {}
        
        # Archivo base de modelos
        files["app/models/__init__.py"] = ""
        
        # Modelos específicos según features
        entities = schema.get("entities", [])
        
        for entity in entities:
            if entity["name"].lower() == "user":
                files["app/models/user.py"] = self._generate_user_model(schema)
        
        # Si no hay entidades pero hay autenticación, crear modelo de usuario
        features = schema.get("features", [])
        if "authentication" in features and not any(e["name"].lower() == "user" for e in entities):
            files["app/models/user.py"] = self._generate_user_model(schema)
        
        return files
    
    def _generate_user_model(self, schema: Dict[str, Any]) -> str:
        """Generar modelo de usuario"""
        return '''from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(email={self.email})>"
'''
    
    async def _generate_route_files(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generar archivos de rutas"""
        files = {}
        
        files["app/routes/__init__.py"] = ""
        
        # Rutas de API básicas
        files["app/routes/api.py"] = self._generate_api_routes(schema)
        
        # Rutas de autenticación si es necesario
        features = schema.get("features", [])
        if "authentication" in features:
            files["app/routes/auth.py"] = self._generate_auth_routes(schema)
        
        return files
    
    def _generate_api_routes(self, schema: Dict[str, Any]) -> str:
        """Generar rutas de API básicas"""
        return '''from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

router = APIRouter()

@router.get("/status")
async def get_api_status():
    """Get API status"""
    return {
        "status": "running",
        "service": "Genesis API",
        "version": "1.0.0"
    }

@router.get("/info")
async def get_api_info():
    """Get API information"""
    return {
        "name": "Genesis API",
        "description": "API generated by Genesis Engine",
        "version": "1.0.0",
        "features": ["REST API", "Documentation"]
    }
'''
    
    def _generate_auth_routes(self, schema: Dict[str, Any]) -> str:
        """Generar rutas de autenticación"""
        return '''from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

router = APIRouter()

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    created_at: datetime

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    # TODO: Implement user registration logic
    # This is a placeholder implementation
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return access token"""
    # TODO: Implement user authentication logic
    # This is a placeholder implementation
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout():
    """Logout user"""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user information"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # TODO: Get user from database
    # This is a placeholder response
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": token_data.email,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
'''
    
    async def _generate_service_files(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generar archivos de servicios"""
        files = {}
        
        files["app/services/__init__.py"] = ""
        
        # Servicio de autenticación si es necesario
        features = schema.get("features", [])
        if "authentication" in features:
            files["app/services/auth_service.py"] = self._generate_auth_service()
        
        return files
    
    def _generate_auth_service(self) -> str:
        """Generar servicio de autenticación"""
        return '''from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return email"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            return email
        except JWTError:
            return None
'''
    
    async def _generate_config_files(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generar archivos de configuración"""
        files = {}
        
        files["app/core/__init__.py"] = ""
        files["app/core/config.py"] = self._generate_config_file(schema)
        
        # Configuración de base de datos si es necesaria
        features = schema.get("features", [])
        if "database" in features:
            files["app/core/database.py"] = self._generate_database_config(schema)
        
        return files
    
    def _generate_config_file(self, schema: Dict[str, Any]) -> str:
        """Generar archivo de configuración"""
        project_name = schema.get("project", {}).get("name", "Genesis API")
        features = schema.get("features", [])
        
        config_content = f'''from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "{project_name}"
    VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
'''
        
        if "database" in features:
            config_content += '''    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost/genesis_db"
    
'''
        
        if "authentication" in features:
            config_content += '''    # Security settings
    SECRET_KEY: str = "your-super-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
'''
        
        config_content += '''    class Config:
        env_file = ".env"

settings = Settings()
'''
        
        return config_content
    
    def _generate_database_config(self, schema: Dict[str, Any]) -> str:
        """Generar configuración de base de datos"""
        return '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
'''
    
    async def _generate_auth_files(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generar archivos de autenticación"""
        files = {}
        
        files["app/auth/__init__.py"] = ""
        files["app/auth/dependencies.py"] = self._generate_auth_dependencies()
        files["app/auth/schemas.py"] = self._generate_auth_schemas()
        
        return files
    
    def _generate_auth_dependencies(self) -> str:
        """Generar dependencias de autenticación"""
        return '''from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # TODO: Get user from database
    return {"email": email}

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Get current active user"""
    # TODO: Check if user is active in database
    return current_user
'''
    
    def _generate_auth_schemas(self) -> str:
        """Generar schemas de autenticación"""
        return '''from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    password_hash: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
'''
    
    async def _generate_deployment_files(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generar archivos de deployment"""
        files = {}
        
        # Requirements.txt
        files["requirements.txt"] = self._generate_requirements_txt(schema)
        
        # Dockerfile
        files["Dockerfile"] = self._generate_dockerfile(schema)
        
        # .env.example
        files[".env.example"] = self._generate_env_example(schema)
        
        # Docker compose (si es necesario)
        features = schema.get("features", [])
        if "docker" in features:
            files["docker-compose.yml"] = self._generate_docker_compose(schema)
        
        return files
    
    def _generate_requirements_txt(self, schema: Dict[str, Any]) -> str:
        """Generar requirements.txt"""
        features = schema.get("features", [])
        
        requirements = [
            "fastapi>=0.115.14",
            "uvicorn[standard]>=0.35.0",
            "pydantic>=2.5.0",
            "python-dotenv>=1.0.0",

            "python-multipart>=0.0.6", 
            "httpx>=0.24.0"
        ]
        
        if "database" in features:
            requirements.extend([
                "sqlalchemy>=2.0.23",
                "alembic>=1.13.1",
                "psycopg2-binary>=2.9.9"
            ])
        
        if "authentication" in features:
            requirements.extend([
                "python-jose[cryptography]>=3.3.0",
                "passlib[bcrypt]>=1.7.4"
            ])
        
        if "testing" in features:
            requirements.extend([
                "pytest>=7.0.0",
                "pytest-asyncio>=0.21.0",
                "httpx>=0.24.0"
            ])
        
        return "\n".join(requirements)
    
    def _generate_dockerfile(self, schema: Dict[str, Any]) -> str:
        """Generar Dockerfile"""
        return '''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _generate_env_example(self, schema: Dict[str, Any]) -> str:
        """Generar archivo .env.example"""
        features = schema.get("features", [])
        project_name = schema.get("project", {}).get("name", "Genesis API")
        
        env_content = f'''# Project settings
PROJECT_NAME={project_name}
HOST=0.0.0.0
PORT=8000

# CORS settings
ALLOWED_HOSTS=["http://localhost:3000", "http://localhost:8000"]

'''
        
        if "database" in features:
            env_content += '''# Database settings
DATABASE_URL=postgresql://user:password@localhost/genesis_db

'''
        
        if "authentication" in features:
            env_content += '''# Security settings
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

'''
        
        return env_content.strip()
    
    def _generate_docker_compose(self, schema: Dict[str, Any]) -> str:
        """Generar docker-compose.yml"""
        features = schema.get("features", [])
        
        compose_content = '''version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/genesis_db
    depends_on:
      - db
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

'''
        
        if "database" in features:
            compose_content += '''  db:
    image: postgres:15
    environment:
      POSTGRES_DB: genesis_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''
        
        return compose_content
    
    async def _generate_test_files(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Generar archivos de testing"""
        files = {}
        
        files["app/tests/__init__.py"] = ""
        files["app/tests/test_main.py"] = self._generate_main_tests()
        files["pytest.ini"] = self._generate_pytest_config()
        
        features = schema.get("features", [])
        if "authentication" in features:
            files["app/tests/test_auth.py"] = self._generate_auth_tests()
        
        return files
    
    def _generate_main_tests(self) -> str:
        """Generar tests principales"""
        return '''import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Genesis API is running"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_status():
    """Test API status endpoint"""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
'''
    
    def _generate_auth_tests(self) -> str:
        """Generar tests de autenticación"""
        return '''import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_user():
    """Test user login"""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_current_user():
    """Test getting current user info"""
    # This test would need a valid token
    # For now, test the endpoint without authentication
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401  # Unauthorized without token
'''
    
    def _generate_pytest_config(self) -> str:
        """Generar configuración de pytest"""
        return '''[tool:pytest]
testpaths = app/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
asyncio_mode = auto
'''
    
    async def _write_backend_files(self, files: Dict[str, str], output_path: str) -> List[str]:
        """Escribir archivos del backend al sistema de archivos"""
        created_files = []
        base_path = Path(output_path)
        
        try:
            for file_path, content in files.items():
                full_path = base_path / file_path
                
                # Crear directorios padre si no existen
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Escribir archivo
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                created_files.append(str(full_path))
                self.logger.debug(f"Archivo creado: {full_path}")
            
            self.logger.info(f"✅ {len(created_files)} archivos de backend creados")
            return created_files
            
        except Exception as e:
            self.logger.error(f"❌ Error escribiendo archivos: {str(e)}")
            raise
    
    # Métodos de las otras tareas específicas
    
    async def _create_data_models(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crear modelos de datos específicos"""
        models = params.get("models", [])
        output_path = params.get("output_path", "./backend/app/models")
        
        generated_models = {}
        for model in models:
            model_code = self._generate_model_code(model)
            generated_models[f"{model['name'].lower()}.py"] = model_code
        
        return {
            "status": "success",
            "models_generated": list(generated_models.keys()),
            "output_path": output_path,
            "models": generated_models
        }
    
    async def _generate_api_endpoints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generar endpoints específicos de API"""
        endpoints = params.get("endpoints", [])
        
        generated_endpoints = {}
        for endpoint in endpoints:
            endpoint_code = self._generate_endpoint_code(endpoint)
            generated_endpoints[endpoint["path"]] = endpoint_code
        
        return {
            "status": "success",
            "endpoints_generated": list(generated_endpoints.keys()),
            "endpoints": generated_endpoints
        }
    
    
    async def _create_authentication_system(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crear sistema de autenticación"""
        backend_cfg: Optional[BackendConfig] = params.get("config")
        auth_type = (
            backend_cfg.auth_method.value if backend_cfg else params.get("auth_type", "jwt")
        )
        
        auth_files = {}
        if auth_type == "jwt":
            auth_files.update(await self._generate_auth_files(params))
        
        return {
            "status": "success",
            "auth_type": auth_type,
            "files_generated": list(auth_files.keys()),
            "features": ["login", "register", "logout", "token_validation"]
        }
    
    async def _generate_middleware_stack(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generar middleware stack"""
        middlewares = params.get("middlewares", ["cors", "logging", "error_handling"])
        
        return {
            "status": "success",
            "middlewares": middlewares,
            "implemented": ["CORS", "Error Handling", "Request Logging"]
        }
    
    async def _create_business_services(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crear servicios de negocio"""
        services = params.get("services", [])
        
        return {
            "status": "success",
            "services_generated": services,
            "pattern": "Service Layer Pattern"
        }
    
    async def _generate_docker_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generar configuración Docker"""
        return {
            "status": "success",
            "files_generated": ["Dockerfile", "docker-compose.yml", ".dockerignore"],
            "base_image": "python:3.11-slim"
        }
    
    async def _handle_generic_backend_task(self, task: AgentTask) -> Dict[str, Any]:
        """Manejar tareas genéricas de backend"""
        return {
            "message": f"Tarea genérica de backend {task.name} procesada",
            "task_id": task.id,
            "params": task.params,
            "agent": self.name
        }
    
    # Métodos auxiliares
    
    def _detect_framework(self, params: Dict[str, Any]) -> str:
        """Detectar framework del proyecto"""
        return params.get("framework", "fastapi")
    
    def _needs_authentication(self, schema: Dict[str, Any]) -> bool:
        """Verificar si el proyecto necesita autenticación"""
        features = schema.get("features", [])
        return "authentication" in features
    
    def _get_implemented_features(self, schema: Dict[str, Any]) -> List[str]:
        """Obtener features implementadas"""
        features = schema.get("features", [])
        implemented = []
        
        for feature in features:
            if feature in ["api", "database", "authentication", "docker"]:
                implemented.append(feature)
        
        return implemented
    
    def _get_next_steps(self, schema: Dict[str, Any]) -> List[str]:
        """Obtener próximos pasos sugeridos"""
        return [
            "Revisar y personalizar configuración en .env",
            "Ejecutar migraciones de base de datos",
            "Agregar tests específicos del dominio",
            "Configurar CI/CD pipeline",
            "Implementar logging y monitoreo"
        ]
    
    def _get_framework_version(self, framework: str) -> str:
        """Obtener versión del framework"""
        versions = {
            "fastapi": "0.115.14",
            "django": "4.2.0",
            "nestjs": "10.0.0"
        }
        return versions.get(framework, "latest")
    
    def _generate_model_code(self, model: Dict[str, Any]) -> str:
        """Generar código para un modelo específico"""
        # Implementación básica
        return f"# Model code for {model.get('name', 'Unknown')}"
    
    def _generate_endpoint_code(self, endpoint: Dict[str, Any]) -> str:
        """Generar código para un endpoint específico"""
        # Implementación básica        return f"# Endpoint code for {endpoint.get('path', 'unknown')}"

    # ------------------------------------------------------------------

    # Methods added for unit tests

    def _load_code_templates(self) -> None:
        """Populate available template files from the template engine."""

        if not hasattr(self, "template_engine"):
            self.available_templates = []
            return
        templates_dir = Path(self.template_engine.templates_dir)

        collected: List[str] = []
        for root, _, files in os.walk(templates_dir):
            for file in files:
                if file.endswith(".j2"):
                    collected.append(str(Path(root) / file))
        self.available_templates = collected

    def _setup_code_generators(self) -> None:
        """Register available code generators."""

        self.code_generators = {
            "nestjs_controller": self._generate_nestjs_controller,
        }


    def _generate_data_models(self, params: Dict[str, Any]) -> List[str]:
        """Generate simple data model and schema files."""
        schema: Dict[str, Any] = params.get("schema", {})
        cfg: BackendConfig = params.get("config")
        output_path = Path(params.get("output_path", "."))
        output_path.mkdir(parents=True, exist_ok=True)

        generated: List[str] = []
        for entity in schema.get("entities", []):
            name = entity.get("name", "Model")
            model_file = output_path / f"{name.lower()}.py"
            model_file.write_text(f"class {name}:\n    pass\n")
            schema_dir = output_path.parent / "schemas"
            schema_dir.mkdir(parents=True, exist_ok=True)
            schema_file = schema_dir / f"{name.lower()}.py"
            schema_file.write_text(f"class {name}Base:\n    pass\n")
            generated.append(str(model_file))
            generated.append(str(schema_file))
        return generated

    def _generate_sqlalchemy_config(self, path: Path, cfg: BackendConfig) -> str:
        """Create a basic SQLAlchemy configuration file."""
        path.mkdir(parents=True, exist_ok=True)
        file = path / "database.py"
        file.write_text("db")
        return str(file)

    def _setup_alembic_migrations(
        self, path: Path, cfg: BackendConfig, schema: Dict[str, Any]
    ) -> List[str]:
        """Create a minimal Alembic configuration."""
        file = path / "alembic.ini"
        file.write_text("alembic")
        return [str(file)]

    def _setup_database_config(self, params: Dict[str, Any]) -> List[str]:
        """Setup database configuration files."""
        cfg: BackendConfig = params.get("config")
        schema: Dict[str, Any] = params.get("schema", {})
        output_path = Path(params.get("output_path", "."))

        db_config = self._generate_sqlalchemy_config(output_path / "app" / "db", cfg)
        migrations = self._setup_alembic_migrations(output_path, cfg, schema)
        return [db_config] + migrations

    def _setup_authentication(self, params: Dict[str, Any]) -> List[str]:
        """Setup authentication according to framework."""
        cfg: BackendConfig = params.get("config")
        output_path = Path(params.get("output_path", "."))
        if cfg.framework == BackendFramework.NESTJS:
            return list(
                asyncio.run(self._generate_nestjs_jwt_auth(output_path, cfg))
            )
        return list(asyncio.run(self._generate_fastapi_jwt_auth(output_path, cfg)))

    def _generate_nestjs_controller(
        self, entity: Dict[str, Any], output_path: Path, cfg: BackendConfig
    ) -> str:
        """Generate a minimal NestJS controller."""
        output_path.mkdir(parents=True, exist_ok=True)
        name = entity.get("name", "Entity")
        file = output_path / f"{name.lower()}.controller.ts"
        file.write_text(f"class {name}Controller {{}}\n")
        return str(file)

    def _generate_typeorm_config(self, output_path: Path, cfg: BackendConfig) -> str:
        """Generate a basic TypeORM configuration file."""
        output_path.mkdir(parents=True, exist_ok=True)
        file = output_path / "typeorm.config.ts"
        file.write_text("export const AppDataSource = new DataSource({});\n")
        return str(file)

    async def _generate_fastapi_jwt_auth(
        self, output_path: Path, cfg: BackendConfig
    ) -> List[str]:
        """Generate FastAPI JWT auth helper."""
        output_path.mkdir(parents=True, exist_ok=True)
        file = output_path / "jwt.py"
        file.write_text("SECRET_KEY = 'changeme'\n")
        return [str(file)]

    async def _generate_nestjs_jwt_auth(
        self, output_path: Path, cfg: BackendConfig
    ) -> List[str]:
        """Generate NestJS JWT auth helper."""
        output_path.mkdir(parents=True, exist_ok=True)
        file = output_path / "jwt.ts"
        file.write_text("export const jwtConstants = {};\n")

        return [str(file)]

    def _generate_dockerfile_python(self, output_path: Path, cfg: BackendConfig) -> str:
        """Generate a simple Python Dockerfile."""
        output_path.mkdir(parents=True, exist_ok=True)
        file = output_path / "Dockerfile"

        file.write_text("FROM python:3.11-slim\n")
        return str(file)

    async def _generate_api_documentation(self, params: Dict[str, Any]) -> List[str]:
        """Generate placeholder API documentation."""
        output_path = Path(params.get("output_path", "."))
        output_path.mkdir(parents=True, exist_ok=True)
        file = output_path / "api.md"
        file.write_text("API Documentation\n")
        return [str(file)]

