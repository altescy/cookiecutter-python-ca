import shutil
from pathlib import Path

use_web_api = "{{ cookiecutter.use_web_api }}" == "yes"
use_frontend = "{{ cookiecutter.use_frontend }}" == "yes"
project_slug = "{{ cookiecutter.project_slug }}"

if not use_web_api:
    shutil.rmtree(Path(project_slug) / "interface" / "web")
    shutil.rmtree(Path("tests") / "integration" / "web")
    Path("tests", "integration", "conftest.py").unlink(missing_ok=True)

if not use_frontend or not use_web_api:
    shutil.rmtree(Path("web"), ignore_errors=True)
