from pathlib import Path
import asyncio

import sys

# Ensure repo root on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.agents.backend import (
    BackendAgent,
    BackendConfig,
    BackendFramework,
    DatabaseType,
    AuthMethod,
)
from genesis_engine.templates.engine import TemplateEngine

def make_agent():
    agent = BackendAgent()
    agent.template_engine = TemplateEngine(
        ROOT / 'genesis_engine' / 'templates' / 'backend'
    )
    # Register missing filter used in templates
    agent.template_engine.register_filter('sql_type', agent.template_engine._get_sql_type)
    agent.template_engine.register_filter('python_type', agent.template_engine._get_python_type)
    return agent


def test_generate_data_models(tmp_path):
    agent = make_agent()
    schema = {
        'entities': [
            {
                'name': 'User',
                'attributes': {
                    'name': 'string',
                    'email': 'email',
                },
            }
        ]
    }
    config = BackendConfig(
        framework=BackendFramework.FASTAPI,
        database=DatabaseType.POSTGRESQL,
        auth_method=AuthMethod.JWT,
        features=[],
        dependencies=[],
        environment_vars={},
    )
    output = tmp_path / 'models'
    output.mkdir(parents=True, exist_ok=True)
    params = {'schema': schema, 'config': config, 'output_path': output}
    generated = agent._generate_data_models(params)
    expected_model = output / 'user.py'
    expected_schema = output.parent / 'schemas' / 'user.py'
    assert list(map(Path, generated)) == [expected_model, expected_schema]
    assert 'class User' in expected_model.read_text()
    assert 'class UserBase' in expected_schema.read_text()


def test_setup_database_config(tmp_path, monkeypatch):
    agent = make_agent()
    config = BackendConfig(
        framework=BackendFramework.FASTAPI,
        database=DatabaseType.POSTGRESQL,
        auth_method=AuthMethod.JWT,
        features=[],
        dependencies=[],
        environment_vars={},
    )
    schema = {'entities': [{'name': 'User'}]}

    def fake_generate_sqlalchemy_config(path, cfg):
        path.mkdir(parents=True, exist_ok=True)
        file = path / 'database.py'
        file.write_text('db')
        return str(file)

    def fake_setup_alembic_migrations(path, cfg, sch):
        file = path / 'alembic.ini'
        file.write_text('alembic')
        return [str(file)]

    monkeypatch.setattr(agent, '_generate_sqlalchemy_config', fake_generate_sqlalchemy_config)
    monkeypatch.setattr(agent, '_setup_alembic_migrations', fake_setup_alembic_migrations)

    params = {'config': config, 'schema': schema, 'output_path': tmp_path}
    generated = agent._setup_database_config(params)

    db_config_file = tmp_path / 'app' / 'db' / 'database.py'
    migration_file = tmp_path / 'alembic.ini'
    assert list(map(Path, generated)) == [db_config_file, migration_file]
    assert db_config_file.read_text() == 'db'
    assert migration_file.read_text() == 'alembic'


def test_setup_authentication(tmp_path, monkeypatch):
    agent = make_agent()
    config = BackendConfig(
        framework=BackendFramework.FASTAPI,
        database=DatabaseType.POSTGRESQL,
        auth_method=AuthMethod.JWT,
        features=[],
        dependencies=[],
        environment_vars={},
    )

    async def fake_generate_fastapi_jwt_auth(path, cfg):
        path.mkdir(parents=True, exist_ok=True)
        file = path / 'jwt.py'
        file.write_text('auth')
        return [str(file)]

    monkeypatch.setattr(agent, '_generate_fastapi_jwt_auth', fake_generate_fastapi_jwt_auth)

    params = {'config': config, 'output_path': tmp_path}
    generated = agent._setup_authentication(params)

    expected_file = tmp_path / 'jwt.py'
    assert list(map(Path, generated)) == [expected_file]
    assert expected_file.read_text() == 'auth'


def test_load_framework_configs():
    agent = make_agent()
    configs = agent.framework_configs
    assert 'fastapi' in configs
    assert 'nestjs' in configs


def test_load_code_templates():
    agent = make_agent()
    agent._load_code_templates()
    assert any(t.endswith('main.py.j2') for t in agent.available_templates)


def test_setup_code_generators():
    agent = make_agent()
    agent._setup_code_generators()
    assert 'nestjs_controller' in agent.code_generators
    assert agent.code_generators['nestjs_controller'] == agent._generate_nestjs_controller


def test_generate_nestjs_controller(tmp_path):
    agent = make_agent()
    config = BackendConfig(
        framework=BackendFramework.NESTJS,
        database=DatabaseType.POSTGRESQL,
        auth_method=AuthMethod.JWT,
        features=[],
        dependencies=[],
        environment_vars={},
    )
    entity = {'name': 'User', 'attributes': {}}
    path = agent._generate_nestjs_controller(entity, tmp_path, config)
    file = Path(path)
    assert file.exists()
    assert 'class UserController' in file.read_text()


def test_generate_typeorm_config(tmp_path):
    agent = make_agent()
    config = BackendConfig(
        framework=BackendFramework.NESTJS,
        database=DatabaseType.POSTGRESQL,
        auth_method=AuthMethod.JWT,
        features=[],
        dependencies=[],
        environment_vars={'ENTITIES': ['User']},
    )
    path = agent._generate_typeorm_config(tmp_path, config)
    file = Path(path)
    assert file.exists()
    assert 'DataSource' in file.read_text()


def test_generate_fastapi_jwt_auth(tmp_path):
    agent = make_agent()
    config = BackendConfig(
        framework=BackendFramework.FASTAPI,
        database=DatabaseType.POSTGRESQL,
        auth_method=AuthMethod.JWT,
        features=[],
        dependencies=[],
        environment_vars={},
    )
    paths = asyncio.run(agent._generate_fastapi_jwt_auth(tmp_path, config))
    file = tmp_path / 'jwt.py'
    assert list(map(Path, paths)) == [file]
    assert 'SECRET_KEY' in file.read_text()


def test_generate_nestjs_jwt_auth(tmp_path):
    agent = make_agent()
    config = BackendConfig(
        framework=BackendFramework.NESTJS,
        database=DatabaseType.POSTGRESQL,
        auth_method=AuthMethod.JWT,
        features=[],
        dependencies=[],
        environment_vars={},
    )
    paths = asyncio.run(agent._generate_nestjs_jwt_auth(tmp_path, config))
    file = tmp_path / 'jwt.ts'
    assert list(map(Path, paths)) == [file]
    assert 'jwtConstants' in file.read_text()


def test_generate_dockerfile_python(tmp_path):
    agent = make_agent()
    config = BackendConfig(
        framework=BackendFramework.FASTAPI,
        database=DatabaseType.POSTGRESQL,
        auth_method=AuthMethod.JWT,
        features=[],
        dependencies=[],
        environment_vars={'PROJECT_NAME': 'demo'},
    )
    path = agent._generate_dockerfile_python(tmp_path, config)
    file = Path(path)
    assert file.exists()
    assert 'FROM python' in file.read_text()


def test_generate_api_documentation(tmp_path):
    agent = make_agent()
    config = BackendConfig(
        framework=BackendFramework.FASTAPI,
        database=DatabaseType.POSTGRESQL,
        auth_method=AuthMethod.JWT,
        features=[],
        dependencies=[],
        environment_vars={},
    )
    params = {'schema': {}, 'config': config, 'output_path': tmp_path}
    paths = asyncio.run(agent._generate_api_documentation(params))
    file = tmp_path / 'api.md'
    assert list(map(Path, paths)) == [file]
    assert 'API Documentation' in file.read_text()


def test_generate_config_file_uses_pydantic_settings():
    agent = make_agent()
    schema = {'project': {'name': 'Demo'}, 'features': []}
    config_content = agent._generate_config_file(schema)
    assert 'from pydantic_settings import BaseSettings' in config_content

