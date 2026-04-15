"""Sector report PDF renderer — Jinja2 + weasyprint."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_sector_report(data: dict) -> bytes:
    """Sektör raporu HTML'ini üret, weasyprint ile PDF'e çevir ve bytes döndür."""
    from weasyprint import HTML  # lazy import — module load süresini kısa tut

    template = _env.get_template("sector_report.html")
    html = template.render(**data)
    return HTML(string=html).write_pdf()
