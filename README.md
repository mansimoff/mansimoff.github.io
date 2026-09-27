# resume-site

Исходники личного сайта-резюме. HTML не редактируется руками — он рендерится
из `data/resume.yaml` через `build.py`. 

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build.py
python -m http.server -d public 8080   # локальный просмотр на :8080
```

Структура:

```
data/resume.yaml       — весь контент (правь только этот файл)
templates/index.html.j2 — HTML-шаблон (структура, не контент)
static/                — CSS, favicon, og-image → копируются в public/ как есть
resume.typ              — исходник PDF-версии (Typst)
build.py                — сборщик YAML+шаблон → public/index.html
.github/workflows/      — CI: сборка + деплой на GitHub Pages при push в main
```
