#!/usr/bin/env python3
"""
build.py — собирает public/index.html (RU) и public/en/index.html (EN)
из data/resume.ru.yaml / data/resume.en.yaml + templates/index.html.j2,
и копирует статику (css/svg/png) в public/.

Запуск локально:
    pip install -r requirements.txt
    python build.py

Результат — в ./public. Смотреть локально:
    python -m http.server -d public 8080
"""

import shutil
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
OUTPUT_DIR = ROOT / "public"

SITE_URL = "https://mansimoff.github.io"   # TODO: подставь свой домен

# Текст интерфейса шаблона (заголовки разделов, кнопки) — не личные данные,
# поэтому живёт здесь одним словарём, а не дублируется в каждом resume.*.yaml.
# Добавишь третий язык — просто допиши сюда третий ключ.
UI_STRINGS = {
    "ru": {
        "download": "Скачать PDF",
        "portfolio": "Портфолио",
        "about": "Обо мне",
        "skills": "Стек",
        "experience": "Опыт",
        "projects": "Проекты",
        "education": "Образование",
        "contacts": "Контакты",
        "github": "ГитХаб",
        "telegram": "Телеграм",
        "email": "Почта",
    },
    "en": {
        "download": "Download PDF",
        "portfolio": "Portfolio",
        "about": "About",
        "skills": "Stack",
        "experience": "Experience",
        "projects": "Projects",
        "education": "Education",
        "contacts": "Contacts",
        "github": "GitHub",
        "telegram": "Telegram",
        "email": "Email",
    },
}

# lang -> (data-файл, путь вывода относительно public/, OG-локаль, canonical URL)
LOCALES = {
    "ru": {
        "data_file": DATA_DIR / "resume.ru.yaml",
        "out_path": OUTPUT_DIR / "index.html",
        "og_locale": "ru_RU",
        "canonical_url": f"{SITE_URL}/",
    },
    "en": {
        "data_file": DATA_DIR / "resume.en.yaml",
        "out_path": OUTPUT_DIR / "en" / "index.html",
        "og_locale": "en_US",
        "canonical_url": f"{SITE_URL}/en/",
    },
}


def load_data(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"Не найден {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def render_html(env: Environment, lang: str, cfg: dict, data: dict) -> str:
    template = env.get_template("index.html.j2")
    return template.render(
        lang=lang,
        t=UI_STRINGS[lang],
        og_locale=cfg["og_locale"],
        canonical_url=cfg["canonical_url"],
        **data,
    )


def copy_static() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, OUTPUT_DIR, dirs_exist_ok=True)


def main() -> None:
    copy_static()  # один раз — общая статика (css/шрифты/фавикон) для обеих версий

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )

    all_data = {lang: load_data(cfg["data_file"]) for lang, cfg in LOCALES.items()}

    # Защита от бага "всегда скачивается не тот язык": если resume_pdf совпадает
    # в нескольких resume.<lang>.yaml, при компиляции PDF в CI один язык молча
    # перезапишет файл другого (см. .github/workflows/deploy.yml, шаг Compile PDFs).
    # Лучше упасть здесь явно, чем ловить на проде "всегда скачивается английский".
    seen: dict[str, str] = {}
    for lang, data in all_data.items():
        name = data["resume_pdf"]
        if name in seen:
            sys.exit(
                f"resume_pdf совпадает у {seen[name]} и {lang}: '{name}'. "
                f"Дай каждому языку своё имя PDF в data/resume.{{lang}}.yaml."
            )
        seen[name] = lang

    for lang, cfg in LOCALES.items():
        html = render_html(env, lang, cfg, all_data[lang])
        cfg["out_path"].parent.mkdir(parents=True, exist_ok=True)
        cfg["out_path"].write_text(html, encoding="utf-8")
        print(f"OK [{lang}]: {cfg['out_path']}")


if __name__ == "__main__":
    main()