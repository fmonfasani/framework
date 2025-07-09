from pathlib import Path
import sys
import asyncio

import types

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from genesis_engine.templates.engine import TemplateEngine


def test_generate_project(tmp_path: Path):
    # Create temporary templates structure
    templates_dir = tmp_path / "templates"
    template_root = templates_dir / "sample"
    sub_dir = template_root / "sub"
    sub_dir.mkdir(parents=True, exist_ok=True)

    # Create template files
    (template_root / "file.txt.j2").write_text("Hello {{ name }}!")
    (sub_dir / "inner.txt.j2").write_text("Inner {{ name }}")
    # Non-template file should be copied directly
    (template_root / "static.txt").write_text("STATIC")

    engine = TemplateEngine(templates_dir)

    out_dir = tmp_path / "output"
    generated = engine.generate_project("sample", out_dir, {"name": "World"})

    expected_files = {
        out_dir / "file.txt",
        out_dir / "sub" / "inner.txt",
        out_dir / "static.txt",
    }
    assert set(map(Path, generated)) == expected_files

    assert (out_dir / "file.txt").read_text() == "Hello World!"
    assert (out_dir / "sub" / "inner.txt").read_text() == "Inner World"
    assert (out_dir / "static.txt").read_text() == "STATIC"


def test_render_template_windows_style(tmp_path: Path):
    templates_dir = tmp_path / "templates"
    sub_dir = templates_dir / "dir"
    sub_dir.mkdir(parents=True, exist_ok=True)
    (sub_dir / "file.txt.j2").write_text("Hello {{ name }}!")

    engine = TemplateEngine(templates_dir)

    content = engine.render_template("dir\\file.txt.j2", {"name": "Bob"})
    assert content == "Hello Bob!"


def test_generate_project_in_event_loop(tmp_path: Path):
    templates_dir = tmp_path / "templates"
    template_root = templates_dir / "sample"
    sub_dir = template_root / "sub"
    sub_dir.mkdir(parents=True, exist_ok=True)

    (template_root / "file.txt.j2").write_text("Hello {{ name }}!")
    (sub_dir / "inner.txt.j2").write_text("Inner {{ name }}")
    (template_root / "static.txt").write_text("STATIC")

    engine = TemplateEngine(templates_dir)

    out_dir = tmp_path / "output_async"
    generated = engine.generate_project("sample", out_dir, {"name": "World"})

    expected_files = {
        out_dir / "file.txt",
        out_dir / "sub" / "inner.txt",
        out_dir / "static.txt",
    }
    assert set(map(Path, generated)) == expected_files
    assert (out_dir / "file.txt").read_text() == "Hello World!"
    assert (out_dir / "sub" / "inner.txt").read_text() == "Inner World"
    assert (out_dir / "static.txt").read_text() == "STATIC"



def test_missing_required_variables_render(tmp_path: Path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "file.txt.j2").write_text("{{ project_name }} {{ description }}")

    engine = TemplateEngine(templates_dir)

    with pytest.raises(ValueError):
        asyncio.run(engine.render_template("file.txt.j2", {"description": "test"}))


def test_missing_required_variables_generate(tmp_path: Path):
    templates_dir = tmp_path / "templates"
    template_root = templates_dir / "sample"
    template_root.mkdir(parents=True)
    (template_root / "file.txt.j2").write_text("{{ project_name }} {{ description }}")

    engine = TemplateEngine(templates_dir)
    out_dir = tmp_path / "out"

    with pytest.raises(ValueError):
        asyncio.run(engine.generate_project("sample", out_dir, {"project_name": "demo"}))

