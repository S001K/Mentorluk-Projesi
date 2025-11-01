"""
Template Manager

Initializes and exports a single, shared Jinja2 environment
for the entire application.
"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .logging import logger

try:
    BASE_DIR = Path(__file__).resolve().parent.parent
    TEMPLATES_DIR = BASE_DIR / "prompt_templates"

    template_loader = FileSystemLoader(searchpath=TEMPLATES_DIR)

    jinja_env = Environment(
        loader=template_loader,
        autoescape=select_autoescape(['html', 'xml'])
    )

    logger.info(f"Jinja2 environment initialized. Loading templates from: {TEMPLATES_DIR}")

except Exception as e:
    logger.error(f"Failed to initialize Jinja2 environment: {e}", exc_info=True)
    raise