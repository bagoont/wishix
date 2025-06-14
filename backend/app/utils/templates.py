from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import BASE_DIR

env = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    autoescape=select_autoescape(
        ["html"],
    ),
)


def render_template(name: str, **kwargs: Any) -> str:
    return env.get_template(name).render(**kwargs)
