#!/usr/bin/env python3
"""
check_syntax.py — быстрая проверка СИНТАКСИСА (не стиля и не полноценный линт)
для всех типов файлов в проекте, перед сборкой/деплоем в CI.

Установка:
    pip install -r requirements.txt   # PyYAML, Jinja2 уже там; + tinycss2

Запуск:
    python check_syntax.py            # yaml/py/css/typ/jinja — можно до build.py
    python check_syntax.py --html     # + собранный public/*.html — только после build.py

Падает с exit code 1 и списком всех найденных ошибок разом (не на первой),
чтобы за один прогон CI увидеть все проблемы, а не чинить по одной.
"""

import argparse
import glob
import re
import subprocess
import sys
from pathlib import Path

import tinycss2
import yaml
from jinja2 import Environment, TemplateSyntaxError

ROOT = Path(__file__).parent
errors: list[str] = []


def check_yaml() -> None:
    for f in sorted(glob.glob("data/*.yaml")) + sorted(glob.glob(".github/**/*.yml", recursive=True)):
        try:
            yaml.safe_load(Path(f).read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            errors.append(f"[YAML] {f}:\n{e}")


def check_python() -> None:
    for f in sorted(glob.glob("*.py")):
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", f],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            errors.append(f"[PY] {f}:\n{result.stderr.strip()}")


def check_css() -> None:
    # Важно: сам по себе CSS-парсер по спецификации ОБЯЗАН молча "чинить"
    # незакрытые блоки на EOF (error recovery — часть стандарта CSS Syntax),
    # поэтому tinycss2 не увидит забытую "}" — самую частую ручную опечатку.
    # Ловим её отдельно, грубым подсчётом скобок вне строк/комментариев —
    # это надёжнее, чем полагаться тут на "правильный" парсер.
    for f in sorted(glob.glob("static/*.css")):
        content = Path(f).read_text(encoding="utf-8")

        stripped = re.sub(r"/\*.*?\*/", "", content, flags=re.S)
        stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', stripped)
        stripped = re.sub(r"'(?:[^'\\]|\\.)*'", "''", stripped)

        depth = 0
        for ch in stripped:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    errors.append(f"[CSS] {f}: лишняя закрывающая '}}' (скобки не сбалансированы)")
                    break
        else:
            if depth != 0:
                errors.append(f"[CSS] {f}: не хватает {depth} закрывающей(их) '}}' — скобки не сбалансированы")

        # tinycss2 — доп. слой поверх: ловит часть ошибок внутри самих правил
        # (то, что не связано с балансом скобок)
        rules = tinycss2.parse_stylesheet(content, skip_comments=True, skip_whitespace=True)
        for rule in rules:
            if rule.type == "error":
                errors.append(f"[CSS] {f} (offset {rule.source_line}:{rule.source_column}):\n{rule.message}")


def check_jinja_templates() -> None:
    # Проверяем ТОЛЬКО синтаксис Jinja (баланс {% %}/{{ }}), не HTML —
    # в .j2-файле валидного HTML ещё нет, там плейсхолдеры вместо контента.
    env = Environment()
    for f in sorted(glob.glob("templates/*.j2")):
        source = Path(f).read_text(encoding="utf-8")
        try:
            env.parse(source)
        except TemplateSyntaxError as e:
            errors.append(f"[JINJA] {f}:{e.lineno}:\n{e.message}")


def check_typst() -> None:
    for f in sorted(glob.glob("*.typ")):
        # Компилируем в никуда — нужен только код возврата.
        # Предупреждения о шрифтах (если static/assets/fonts/ пуст локально)
        # не считаются ошибкой синтаксиса — типографика не наша забота здесь.
        result = subprocess.run(
            ["typst", "compile", f, "/tmp/_syntax_check.pdf", "--font-path", "static/assets/fonts"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            errors.append(f"[TYPST] {f}:\n{result.stderr.strip()}")


def check_rendered_html() -> None:
    files = sorted(glob.glob("public/**/*.html", recursive=True))
    if not files:
        errors.append("[HTML] public/ пуст — запусти build.py перед --html")
        return
    for f in files:
        result = subprocess.run(
            ["tidy", "-q", "-errors", f],
            capture_output=True, text=True,
        )
        # tidy: 0 — без замечаний, 1 — есть warnings (не блокируем), 2 — реальные ошибки
        if result.returncode >= 2:
            errors.append(f"[HTML] {f}:\n{result.stderr.strip()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", action="store_true", help="также проверить public/*.html (нужен собранный public/)")
    args = parser.parse_args()

    check_yaml()
    check_python()
    check_css()
    check_jinja_templates()
    check_typst()
    if args.html:
        check_rendered_html()

    if errors:
        print("\n\n".join(errors), file=sys.stderr)
        print(f"\n--- {len(errors)} ошибка(ок) ---", file=sys.stderr)
        sys.exit(1)

    print("OK: синтаксис всех проверенных файлов корректен")


if __name__ == "__main__":
    main()