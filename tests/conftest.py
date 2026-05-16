from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter

TEMPLATE_DIR = Path(__file__).parent.parent
DEFAULT_CONTEXT = {"project_name": "test app"}


@pytest.fixture
def bake(tmp_path: Path):
    def _bake(**extra_context: str) -> Path:
        cookiecutter(
            str(TEMPLATE_DIR),
            no_input=True,
            extra_context={**DEFAULT_CONTEXT, **extra_context},
            output_dir=str(tmp_path),
        )
        return tmp_path / "test_app"

    return _bake
