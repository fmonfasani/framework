"""
AI Ready Agent - Preparación para integración con IA

Este agente es responsable de:
- Integración con LLMs (OpenAI, Anthropic, Cohere)
- Configuración de vector stores (Pinecone, Weaviate, Chroma)
- Implementación de RAG (Retrieval Augmented Generation)
- Configuración de embeddings
- Implementación de chat/asistentes IA
- Integración con APIs de IA
- Configuración de prompts y templates
- Implementación de AI workflows
- Preparación para fine-tuning
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass

# Imports para IA - pueden no estar disponibles en todas las instalaciones
try:  # pragma: no cover - opcional según entorno
    import openai
    OPENAI_AVAILABLE = True
except Exception:  # noqa: W0703 - cualquier error al importar
    OPENAI_AVAILABLE = False

try:  # pragma: no cover - opcional según entorno
    import anthropic
    ANTHROPIC_AVAILABLE = True
except Exception:  # noqa: W0703
    ANTHROPIC_AVAILABLE = False

from genesis_engine.mcp.agent_base import GenesisAgent, AgentTask, TaskResult
from genesis_templates.engine import TemplateEngine


def _check_import(module_name: str) -> bool:
    """Verificar si un módulo se puede importar"""
    try:  # pragma: no cover - import check
        __import__(module_name)
        return True
    except ImportError:
        return False


def check_ai_dependencies() -> Dict[str, bool]:
    """Verificar dependencias de IA disponibles"""
    return {
        "openai": OPENAI_AVAILABLE,
        "anthropic": ANTHROPIC_AVAILABLE,
        "transformers": _check_import("transformers"),
        "langchain": _check_import("langchain"),
        "chromadb": _check_import("chromadb"),
        "pinecone": _check_import("pinecone"),
        "weaviate": _check_import("weaviate"),
    }

class LLMProvider(str, Enum):
    """Proveedores de LLM"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"

class VectorStore(str, Enum):
    """Stores de vectores"""
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    CHROMA = "chroma"
    QDRANT = "qdrant"
    FAISS = "faiss"
    PGVECTOR = "pgvector"

class AIFeature(str, Enum):
    """Características de IA"""
    CHAT_ASSISTANT = "chat_assistant"
    RAG_SYSTEM = "rag_system"
    CONTENT_GENERATION = "content_generation"
    DOCUMENT_ANALYSIS = "document_analysis"
    SEMANTIC_SEARCH = "semantic_search"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    AUTO_CATEGORIZATION = "auto_categorization"

@dataclass
class AIConfig:
    """Configuración de IA"""
    llm_provider: LLMProvider
    vector_store: VectorStore
    features: List[AIFeature]
    embedding_model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    enable_streaming: bool = True
    enable_function_calling: bool = True
    custom_prompts: Dict[str, str] = None
    
    def __post_init__(self):
        if self.custom_prompts is None:
            self.custom_prompts = {}

class AIReadyAgent(GenesisAgent):
    """
    Agente AI Ready - Preparación para IA
    
    Configura y prepara el proyecto para integrar capacidades de IA,
    incluyendo LLMs, vector stores, RAG y otros sistemas de IA.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="ai_ready_agent",
            name="AIReadyAgent",
            agent_type="ai_integration"
        )
        
        # Capacidades del agente
        self.add_capability("llm_integration")
        self.add_capability("vector_store_setup")
        self.add_capability("rag_implementation")
        self.add_capability("embedding_pipeline")
        self.add_capability("ai_chat_interface")
        self.add_capability("prompt_engineering")
        self.add_capability("ai_workflow_automation")
        
        # Registrar handlers específicos
        self.register_handler("setup_ai", self._handle_setup_ai)
        self.register_handler("integrate_llm", self._handle_integrate_llm)
        self.register_handler("setup_vector_store", self._handle_setup_vector_store)
        self.register_handler("implement_rag", self._handle_implement_rag)
        self.register_handler("create_chat_interface", self._handle_create_chat_interface)
        self.register_handler("setup_embeddings", self._handle_setup_embeddings)
        
        # Motor de templates
        self.template_engine = TemplateEngine()
        
        # Configuraciones predefinidas
        self.ai_templates = self._load_ai_templates()
        
    async def initialize(self):
        """Inicialización del agente AI Ready"""
        self.logger.info("🧠 Inicializando AI Ready Agent")
        
        # Cargar templates de IA
        await self._load_ai_code_templates()
        
        self.set_metadata("version", "1.0.0")
        self.set_metadata("specialization", "ai_integration")
        
        self.logger.info("✅ AI Ready Agent inicializado")
    
    async def execute_task(self, task: AgentTask) -> Any:
        """Ejecutar tarea específica de IA"""
        task_name = task.name.lower()
        
        if "setup_ai" in task_name:
            return await self._setup_complete_ai_integration(task.params)
        elif "integrate_llm" in task_name:
            return await self._integrate_llm_provider(task.params)
        elif "setup_vector_store" in task_name:
            return await self._setup_vector_database(task.params)
        elif "implement_rag" in task_name:
            return await self._implement_rag_system(task.params)
        elif "create_chat_interface" in task_name:
            return await self._create_chat_interface(task.params)
        elif "setup_embeddings" in task_name:
            return await self._setup_embedding_pipeline(task.params)
        else:
            raise ValueError(f"Tarea no reconocida: {task.name}")
    
    async def _setup_complete_ai_integration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configurar integración completa de IA"""
        self.logger.info("🚀 Configurando integración completa de IA")
        
        project_path = Path(params.get("project_path", "./"))
        schema = params.get("schema", {})
        config = self._extract_ai_config(params)
        
        generated_files = []
        
        # 1. Configurar proveedor LLM
        llm_files = await self._integrate_llm_provider({
            "project_path": project_path,
            "config": config
        })
        generated_files.extend(llm_files)
        
        # 2. Configurar vector store
        vector_files = await self._setup_vector_database({
            "project_path": project_path,
            "config": config
        })
        generated_files.extend(vector_files)
        
        # 3. Implementar pipeline de embeddings
        embedding_files = await self._setup_embedding_pipeline({
            "project_path": project_path,
            "config": config,
            "schema": schema
        })
        generated_files.extend(embedding_files)
        
        # 4. Implementar características específicas
        for feature in config.features:
            if feature == AIFeature.RAG_SYSTEM:
                rag_files = await self._implement_rag_system({
                    "project_path": project_path,
                    "config": config
                })
                generated_files.extend(rag_files)
            
            elif feature == AIFeature.CHAT_ASSISTANT:
                chat_files = await self._create_chat_interface({
                    "project_path": project_path,
                    "config": config
                })
                generated_files.extend(chat_files)
            
            elif feature == AIFeature.SEMANTIC_SEARCH:
                search_files = await self._implement_semantic_search({
                    "project_path": project_path,
                    "config": config
                })
                generated_files.extend(search_files)
        
        # 5. Configurar workflows de IA
        workflow_files = await self._setup_ai_workflows(project_path, config, schema)
        generated_files.extend(workflow_files)
        
        # 6. Generar documentación de IA
        docs_files = await self._generate_ai_documentation(project_path, config)
        generated_files.extend(docs_files)
        
        # 7. Configurar variables de entorno
        env_file = await self._setup_ai_environment_variables(project_path, config)
        generated_files.append(env_file)
        
        result = {
            "llm_provider": config.llm_provider.value,
            "vector_store": config.vector_store.value,
            "features": [f.value for f in config.features],
            "generated_files": generated_files,
            "api_endpoints": self._get_ai_endpoints(config),
            "setup_instructions": self._get_ai_setup_instructions(config)
        }
        
        self.logger.info(f"✅ Integración de IA completada - {len(generated_files)} archivos generados")
        return result
    
    def _extract_ai_config(self, params: Dict[str, Any]) -> AIConfig:
        """Extraer configuración de IA"""
        return AIConfig(
            llm_provider=LLMProvider(params.get("llm_provider", "openai")),
            vector_store=VectorStore(params.get("vector_store", "chroma")),
            features=[AIFeature(f) for f in params.get("features", ["chat_assistant", "rag_system"])],
            embedding_model=params.get("embedding_model", "text-embedding-ada-002"),
            max_tokens=params.get("max_tokens", 4000),
            temperature=params.get("temperature", 0.7),
            enable_streaming=params.get("enable_streaming", True),
            enable_function_calling=params.get("enable_function_calling", True),
            custom_prompts=params.get("custom_prompts", {})
        )
    
    async def _integrate_llm_provider(self, params: Dict[str, Any]) -> List[str]:
        """Integrar proveedor de LLM"""
        self.logger.info("🤖 Integrando proveedor de LLM")
        
        project_path = Path(params.get("project_path", "./"))
        config = params.get("config")
        
        generated_files = []
        backend_path = project_path / "backend"
        
        # Crear directorio de IA
        ai_dir = backend_path / "app" / "ai"
        ai_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar cliente LLM
        llm_client_file = await self._generate_llm_client(ai_dir, config)
        generated_files.append(llm_client_file)
        
        # Generar servicio de chat
        chat_service_file = await self._generate_chat_service(ai_dir, config)
        generated_files.append(chat_service_file)
        
        # Generar utilidades de prompts
        prompt_utils_file = await self._generate_prompt_utilities(ai_dir, config)
        generated_files.append(prompt_utils_file)
        
        # Generar endpoints de IA
        ai_router_file = await self._generate_ai_endpoints(backend_path / "app" / "routes", config)
        generated_files.append(ai_router_file)
        
        return generated_files
    
    async def _setup_vector_database(self, params: Dict[str, Any]) -> List[str]:
        """Configurar base de datos vectorial"""
        self.logger.info("🔍 Configurando vector store")
        
        project_path = Path(params.get("project_path", "./"))
        config = params.get("config")
        
        generated_files = []
        backend_path = project_path / "backend"
        ai_dir = backend_path / "app" / "ai"
        
        # Generar cliente vector store
        vector_client_file = await self._generate_vector_store_client(ai_dir, config)
        generated_files.append(vector_client_file)
        
        # Generar servicio de embeddings
        embedding_service_file = await self._generate_embedding_service(ai_dir, config)
        generated_files.append(embedding_service_file)
        
        # Generar utilidades de búsqueda
        search_utils_file = await self._generate_search_utilities(ai_dir, config)
        generated_files.append(search_utils_file)
        
        return generated_files
    
    async def _implement_rag_system(self, params: Dict[str, Any]) -> List[str]:
        """Implementar sistema RAG"""
        self.logger.info("📚 Implementando sistema RAG")
        
        project_path = Path(params.get("project_path", "./"))
        config = params.get("config")
        
        generated_files = []
        backend_path = project_path / "backend"
        ai_dir = backend_path / "app" / "ai"
        
        # Generar servicio RAG
        rag_service_file = await self._generate_rag_service(ai_dir, config)
        generated_files.append(rag_service_file)
        
        # Generar procesador de documentos
        document_processor_file = await self._generate_document_processor(ai_dir, config)
        generated_files.append(document_processor_file)
        
        # Generar chunking strategies
        chunking_file = await self._generate_chunking_strategies(ai_dir, config)
        generated_files.append(chunking_file)
        
        return generated_files
    
    async def _create_chat_interface(self, params: Dict[str, Any]) -> List[str]:
        """Crear interfaz de chat"""
        self.logger.info("💬 Creando interfaz de chat")
        
        project_path = Path(params.get("project_path", "./"))
        config = params.get("config")
        
        generated_files = []
        frontend_path = project_path / "frontend"
        
        # Generar componente de chat (React)
        chat_component_file = await self._generate_chat_component(frontend_path, config)
        generated_files.append(chat_component_file)
        
        # Generar hook de chat
        chat_hook_file = await self._generate_chat_hook(frontend_path, config)
        generated_files.append(chat_hook_file)
        
        # Generar servicio de chat del frontend
        chat_api_file = await self._generate_frontend_chat_api(frontend_path, config)
        generated_files.append(chat_api_file)
        
        # Generar página de chat
        chat_page_file = await self._generate_chat_page(frontend_path, config)
        generated_files.append(chat_page_file)
        
        return generated_files
    
    async def _generate_llm_client(self, ai_dir: Path, config: AIConfig) -> str:
        """Generar cliente LLM"""
        
        template_vars = {
            "llm_provider": config.llm_provider.value,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "enable_streaming": config.enable_streaming,
            "enable_function_calling": config.enable_function_calling
        }
        
        if config.llm_provider == LLMProvider.OPENAI:
            template_name = "ai/openai_client.py.j2"
        elif config.llm_provider == LLMProvider.ANTHROPIC:
            template_name = "ai/anthropic_client.py.j2"
        else:
            template_name = "ai/generic_llm_client.py.j2"
        
        content = self.template_engine.render_template(template_name, template_vars)
        
        output_file = ai_dir / "llm_client.py"
        output_file.write_text(content)
        
        return str(output_file)
    
    async def _generate_chat_service(self, ai_dir: Path, config: AIConfig) -> str:
        """Generar servicio de chat"""
        
        template_vars = {
            "llm_provider": config.llm_provider.value,
            "enable_streaming": config.enable_streaming,
            "enable_function_calling": config.enable_function_calling,
            "custom_prompts": config.custom_prompts
        }
        
        content = self.template_engine.render_template(
            "ai/chat_service.py.j2",
            template_vars
        )
        
        output_file = ai_dir / "chat_service.py"
        output_file.write_text(content)
        
        return str(output_file)
    
    async def _generate_vector_store_client(self, ai_dir: Path, config: AIConfig) -> str:
        """Generar cliente vector store"""
        
        template_vars = {
            "vector_store": config.vector_store.value,
            "embedding_model": config.embedding_model
        }
        
        if config.vector_store == VectorStore.CHROMA:
            template_name = "ai/chroma_client.py.j2"
        elif config.vector_store == VectorStore.PINECONE:
            template_name = "ai/pinecone_client.py.j2"
        else:
            template_name = "ai/generic_vector_client.py.j2"
        
        content = self.template_engine.render_template(template_name, template_vars)
        
        output_file = ai_dir / "vector_store.py"
        output_file.write_text(content)
        
        return str(output_file)
    
    async def _generate_chat_component(self, frontend_path: Path, config: AIConfig) -> str:
        """Generar componente de chat React"""
        
        template_vars = {
            "enable_streaming": config.enable_streaming,
            "llm_provider": config.llm_provider.value
        }
        
        content = self.template_engine.render_template(
            "ai/react/ChatComponent.tsx.j2",
            template_vars
        )
        
        components_dir = frontend_path / "components" / "ai"
        components_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = components_dir / "ChatComponent.tsx"
        output_file.write_text(content)
        
        return str(output_file)
    
    def _get_ai_endpoints(self, config: AIConfig) -> List[Dict[str, str]]:
        """Obtener endpoints de IA generados"""
        endpoints = [
            {
                "path": "/ai/chat",
                "method": "POST",
                "description": "Enviar mensaje al asistente IA"
            },
            {
                "path": "/ai/chat/stream",
                "method": "POST", 
                "description": "Chat con streaming de respuestas"
            }
        ]
        
        if AIFeature.RAG_SYSTEM in config.features:
            endpoints.extend([
                {
                    "path": "/ai/documents",
                    "method": "POST",
                    "description": "Subir documento para RAG"
                },
                {
                    "path": "/ai/search",
                    "method": "POST",
                    "description": "Búsqueda semántica"
                }
            ])
        
        if AIFeature.SEMANTIC_SEARCH in config.features:
            endpoints.append({
                "path": "/ai/search/semantic",
                "method": "POST",
                "description": "Búsqueda semántica avanzada"
            })
        
        return endpoints
    
    def _get_ai_setup_instructions(self, config: AIConfig) -> List[str]:
        """Obtener instrucciones de configuración"""
        instructions = [
            "1. Configurar variables de entorno de IA en .env",
            f"2. Instalar dependencias: pip install openai chromadb langchain",
            "3. Configurar claves API para el proveedor LLM"
        ]
        
        if config.llm_provider == LLMProvider.OPENAI:
            instructions.append("4. Configurar OPENAI_API_KEY en variables de entorno")
        elif config.llm_provider == LLMProvider.ANTHROPIC:
            instructions.append("4. Configurar ANTHROPIC_API_KEY en variables de entorno")
        
        if config.vector_store == VectorStore.PINECONE:
            instructions.append("5. Configurar PINECONE_API_KEY y PINECONE_INDEX_NAME")
        elif config.vector_store == VectorStore.WEAVIATE:
            instructions.append("5. Configurar WEAVIATE_URL y WEAVIATE_API_KEY")
        
        instructions.extend([
            "6. Ejecutar migraciones si es necesario",
            "7. Probar endpoints de IA: POST /ai/chat",
            "8. Acceder a interfaz de chat: /chat"
        ])
        
        return instructions
    
    # Handlers MCP
    async def _handle_setup_ai(self, request) -> Dict[str, Any]:
        """Handler para configuración completa de IA"""
        return await self._setup_complete_ai_integration(request.params)
    
    async def _handle_integrate_llm(self, request) -> Dict[str, Any]:
        """Handler para integración de LLM"""
        files = await self._integrate_llm_provider(request.params)
        return {"generated_files": files}
    
    async def _handle_setup_vector_store(self, request) -> Dict[str, Any]:
        """Handler para configuración de vector store"""
        files = await self._setup_vector_database(request.params)
        return {"generated_files": files}
    
    async def _handle_implement_rag(self, request) -> Dict[str, Any]:
        """Handler para implementación de RAG"""
        files = await self._implement_rag_system(request.params)
        return {"generated_files": files}
    
    async def _handle_create_chat_interface(self, request) -> Dict[str, Any]:
        """Handler para creación de interfaz de chat"""
        files = await self._create_chat_interface(request.params)
        return {"generated_files": files}
    
    async def _handle_setup_embeddings(self, request) -> Dict[str, Any]:
        """Handler para configuración de embeddings"""
        files = await self._setup_embedding_pipeline(request.params)
        return {"generated_files": files}
    
    # Métodos auxiliares (implementación simplificada)
    def _load_ai_templates(self) -> Dict[str, Any]:
        """Cargar templates de IA"""
        return {
            "chat_prompts": {
                "system_prompt": "You are a helpful AI assistant.",
                "welcome_message": "Hello! How can I help you today?"
            },
            "rag_prompts": {
                "query_prompt": "Based on the following context, answer the question:",
                "no_context_prompt": "I don't have enough context to answer that question."
            }
        }
    
    async def _load_ai_code_templates(self):
        """Cargar templates de código IA"""
        # For the test-suite we simply record which templates are available
        # under the ``ai`` folder of the bundled templates directory.  The
        # :class:`TemplateEngine` already knows how to list templates so we just
        # store the result for potential use by the generator helpers.
        self.available_ai_templates = self.template_engine.list_templates("ai/*")
        return self.available_ai_templates
    
    async def _setup_embedding_pipeline(self, params: Dict[str, Any]) -> List[str]:
        """Configurar pipeline de embeddings"""
        project_path = Path(params.get("project_path", "./"))
        config = params.get("config")

        ai_dir = project_path / "backend" / "app" / "ai"
        ai_dir.mkdir(parents=True, exist_ok=True)

        files = [await self._generate_embedding_service(ai_dir, config)]
        return files
    
    async def _implement_semantic_search(self, params: Dict[str, Any]) -> List[str]:
        """Implementar búsqueda semántica"""
        project_path = Path(params.get("project_path", "./"))
        config = params.get("config")

        ai_dir = project_path / "backend" / "app" / "ai"
        ai_dir.mkdir(parents=True, exist_ok=True)

        search_utils = await self._generate_search_utilities(ai_dir, config)
        return [search_utils]
    
    async def _setup_ai_workflows(self, project_path: Path, config: AIConfig, schema: Dict[str, Any]) -> List[str]:
        """Configurar workflows de IA"""
        workflow_file = project_path / "backend" / "app" / "ai" / "workflows.py"
        workflow_file.parent.mkdir(parents=True, exist_ok=True)
        content = """async def run_workflow(input_text: str) -> str:\n    return input_text\n"""
        await asyncio.to_thread(workflow_file.write_text, content)
        return [str(workflow_file)]
    
    async def _generate_ai_documentation(self, project_path: Path, config: AIConfig) -> List[str]:
        """Generar documentación de IA"""
        docs_dir = project_path / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        doc_file = docs_dir / "AI_README.md"
        content = (
            "# AI Integration\n"
            "This project includes basic AI endpoints and utilities.\n"
        )

        await asyncio.to_thread(doc_file.write_text, content)
        return [str(doc_file)]
    
    async def _setup_ai_environment_variables(self, project_path: Path, config: AIConfig) -> str:
        """Configurar variables de entorno de IA"""
        
        env_content = f"""
# AI Configuration
LLM_PROVIDER={config.llm_provider.value}
VECTOR_STORE={config.vector_store.value}
EMBEDDING_MODEL={config.embedding_model}
MAX_TOKENS={config.max_tokens}
TEMPERATURE={config.temperature}

# API Keys (configure these)
"""
        
        if config.llm_provider == LLMProvider.OPENAI:
            env_content += "OPENAI_API_KEY=your_openai_api_key_here\n"
        elif config.llm_provider == LLMProvider.ANTHROPIC:
            env_content += "ANTHROPIC_API_KEY=your_anthropic_api_key_here\n"
        
        if config.vector_store == VectorStore.PINECONE:
            env_content += "PINECONE_API_KEY=your_pinecone_api_key_here\n"
            env_content += "PINECONE_INDEX_NAME=your_index_name\n"
        
        # Agregar al archivo .env existente
        env_file = project_path / "backend" / ".env"
        if env_file.exists():
            existing_content = env_file.read_text()
            env_file.write_text(existing_content + "\n" + env_content)
        else:
            env_file.write_text(env_content)
        
        return str(env_file)
    
    async def _generate_prompt_utilities(self, ai_dir: Path, config: AIConfig) -> str:
        """Generar utilidades de prompts"""
        prompts = self.ai_templates.get("chat_prompts", {}).copy()
        prompts.update(config.custom_prompts or {})

        content = (
            f"DEFAULT_SYSTEM_PROMPT = {json.dumps(prompts.get('system_prompt', ''))}\n"
            f"WELCOME_MESSAGE = {json.dumps(prompts.get('welcome_message', ''))}\n"
        )

        output_file = ai_dir / "prompts.py"
        await asyncio.to_thread(output_file.write_text, content)
        return str(output_file)
    
    async def _generate_ai_endpoints(self, routes_dir: Path, config: AIConfig) -> str:
        """Generar endpoints de IA"""
        routes_dir.mkdir(parents=True, exist_ok=True)
        output_file = routes_dir / "ai.py"

        content_lines = [
            "from fastapi import APIRouter, UploadFile",
            "from ..ai.chat_service import ChatService",
            "",
            "router = APIRouter()",
            "chat_service = ChatService()",
            "",
            "@router.post('/ai/chat')",
            "async def chat(payload: dict):",
            "    message = payload.get('message', '')",
            "    return await chat_service.chat(message)",
        ]

        if config.enable_streaming:
            content_lines.extend([
                "",
                "@router.post('/ai/chat/stream')",
                "async def chat_stream(payload: dict):",
                "    message = payload.get('message', '')",
                "    return chat_service.chat_stream(message)",
            ])

        if AIFeature.RAG_SYSTEM in config.features:
            content_lines.extend([
                "",
                "@router.post('/ai/documents')",
                "async def upload_document(file: UploadFile):",
                "    # Placeholder for document ingestion",
                "    return {'status': 'uploaded'}",
                "",
                "@router.post('/ai/search')",
                "async def search(payload: dict):",
                "    query = payload.get('query', '')",
                "    return await chat_service.search(query)",
            ])

        if AIFeature.SEMANTIC_SEARCH in config.features:
            content_lines.extend([
                "",
                "@router.post('/ai/search/semantic')",
                "async def semantic_search(payload: dict):",
                "    query = payload.get('query', '')",
                "    return await chat_service.semantic_search(query)",
            ])

        content = "\n".join(content_lines) + "\n"
        await asyncio.to_thread(output_file.write_text, content)
        return str(output_file)
    
    async def _generate_embedding_service(self, ai_dir: Path, config: AIConfig) -> str:
        """Generar servicio de embeddings"""
        output_file = ai_dir / "embedding_service.py"
        lines = [
            "from typing import List",
            "",
            "try:",
            "    import openai",
            "except Exception:",
            "    openai = None",
            "",
            "",
            "class EmbeddingService:",
            f"    def __init__(self, model: str = '{config.embedding_model}'):",
            "        self.model = model",
            "",
            "    async def embed(self, text: str) -> List[float]:",
            "        if openai is None:",
            "            return []",
            "        resp = await openai.Embedding.acreate(input=text, model=self.model)",
            "        return resp['data'][0]['embedding']",
        ]
        await asyncio.to_thread(output_file.write_text, "\n".join(lines) + "\n")
        return str(output_file)
    
    async def _generate_search_utilities(self, ai_dir: Path, config: AIConfig) -> str:
        """Generar utilidades de búsqueda"""
        output_file = ai_dir / "search_utils.py"
        content = (
            "def similarity_search(store, embedding, top_k=5):\n"
            "    return store.similarity_search(embedding, top_k)\n"
        )
        await asyncio.to_thread(output_file.write_text, content)
        return str(output_file)
    
    async def _generate_rag_service(self, ai_dir: Path, config: AIConfig) -> str:
        """Generar servicio RAG"""
        output_file = ai_dir / "rag_service.py"
        content = (
            "class RAGService:\n"
            "    def __init__(self, vector_store, llm_client):\n"
            "        self.vector_store = vector_store\n"
            "        self.llm_client = llm_client\n\n"
            "    async def answer(self, query: str) -> str:\n"
            "        docs = self.vector_store.search(query)\n"
            "        context = '\n'.join(docs)\n"
            "        prompt = f'{context}\n{query}'\n"
            "        return await self.llm_client.chat(prompt)\n"
        )
        await asyncio.to_thread(output_file.write_text, content)
        return str(output_file)
    
    async def _generate_document_processor(self, ai_dir: Path, config: AIConfig) -> str:
        """Generar procesador de documentos"""
        output_file = ai_dir / "document_processor.py"
        content = (
            "def process_document(text: str) -> list[str]:\n"
            "    return [text]\n"
        )
        await asyncio.to_thread(output_file.write_text, content)
        return str(output_file)
    
    async def _generate_chunking_strategies(self, ai_dir: Path, config: AIConfig) -> str:
        """Generar estrategias de chunking"""
        output_file = ai_dir / "chunking.py"
        content = (
            "def chunk_text(text: str, size: int = 500) -> list[str]:\n"
            "    return [text[i:i+size] for i in range(0, len(text), size)]\n"
        )
        await asyncio.to_thread(output_file.write_text, content)
        return str(output_file)
    
    async def _generate_chat_hook(self, frontend_path: Path, config: AIConfig) -> str:
        """Generar hook de chat"""
        hooks_dir = frontend_path / "lib"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        output_file = hooks_dir / "useChat.ts"

        content = (
            "import { useState } from 'react';\n"
            "import { sendChatMessage } from './api/chat';\n\n"
            "export function useChat() {\n"
            "  const [messages, setMessages] = useState<string[]>([]);\n\n"
            "  const send = async (message: string) => {\n"
            "    const res = await sendChatMessage(message);\n"
            "    setMessages([...messages, res.data]);\n"
            "  };\n\n"
            "  return { messages, send };\n"
            "}\n"
        )

        await asyncio.to_thread(output_file.write_text, content)
        return str(output_file)
    
    async def _generate_frontend_chat_api(self, frontend_path: Path, config: AIConfig) -> str:
        """Generar API de chat del frontend"""
        api_dir = frontend_path / "lib" / "api"
        api_dir.mkdir(parents=True, exist_ok=True)
        output_file = api_dir / "chat.ts"

        content = (
            "import { apiClient } from './client';\n\n"
            "export const sendChatMessage = (message: string) =>\n"
            "  apiClient.post('/ai/chat', { message });\n"
        )
        await asyncio.to_thread(output_file.write_text, content)
        return str(output_file)

    async def _generate_chat_page(self, frontend_path: Path, config: AIConfig) -> str:
        """Generar página de chat"""
        page_dir = frontend_path / "app" / "chat"
        page_dir.mkdir(parents=True, exist_ok=True)
        output_file = page_dir / "page.tsx"

        content = (
            "import ChatComponent from '../../components/ai/ChatComponent';\n\n"
            "export default function ChatPage() {\n"
            "  return <ChatComponent />;\n"
            "}\n"
        )
        await asyncio.to_thread(output_file.write_text, content)
        return str(output_file)
