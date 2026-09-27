#!/usr/bin/env python3
"""
build.py — собирает public/index.html из data/resume.yaml + templates/index.html.j2
и копирует статику (css/svg/png) в public/.

Запуск локально:
    pip install -r requirements.txt
    python build.py

Результат появляется в ./public — этот каталог и публикуется на GitHub Pages
(в CI он собирается заново при каждом push, локально можно смотреть через
`python -m http.server -d public 8080`).
"""

import shutil
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "resume.yaml"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
OUTPUT_DIR = ROOT / "public"


def load_data() -> dict:
    if not DATA_FILE.exists():
        sys.exit(f"Не найден {DATA_FILE}")
    with open(DATA_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def render_html(data: dict) -> str:
    # autoescape=True — защита от случайного HTML-инжекта из yaml-полей
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("index.html.j2")
    return template.render(**data)


def copy_static() -> None:
    # Копируем содержимое static/ в корень public/ (не в подпапку static/),
    # чтобы пути вида href="style.css" в шаблоне оставались рабочими.
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, OUTPUT_DIR, dirs_exist_ok=True)


def main() -> None:
    data = load_data()
    copy_static()
    html = render_html(data)
    (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"OK: собрано в {OUTPUT_DIR}/index.html")


if __name__ == "__main__":
    main()
