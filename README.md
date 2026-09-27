# resume-site

Личный сайт-резюме: `https://mansimoff.github.io/`. Русская и английская версии,
PDF для скачивания на обоих языках, всё собирается из пары YAML-файлов через
GitHub Actions.

**Главный принцип проекта:** контент живёт только в `data/resume.ru.yaml` и
`data/resume.en.yaml`. Всё остальное — шаблоны, которые превращают эти данные
в HTML и PDF. Если ты правишь HTML/Typst руками вместо yaml — ты, скорее всего,
делаешь что-то не то (см. раздел «Что можно/нельзя делать» ниже).

---

## Быстрый старт (для тех, кто форкнул репозиторий себе)

```bash
git clone https://github.com/<you>/<you>.github.io.git
cd <you>.github.io
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

1. Отредактируй `data/resume.ru.yaml` и `data/resume.en.yaml` — впиши свои данные
   (см. «Как редактировать контент» ниже)
2. Замени `SITE_URL` в `build.py` на свой домен
3. Собери и посмотри локально:
   ```bash
   python build.py
   python -m http.server -d public 8080
   # открой http://localhost:8080
   ```
4. Настрой GitHub Pages: Settings → Pages → Source → **GitHub Actions**
5. `git push` — CI соберёт сайт и оба PDF автоматически

---

## Как всё устроено (поток данных)

```
data/resume.ru.yaml  ─┐
data/resume.en.yaml  ─┤
                       ├──► build.py ────────► public/index.html   (RU)
                       │                       public/en/index.html (EN)
                       │
                       └──► resume.typ ──────► public/resume_ru.pdf
                            (--input lang=..)   public/resume_en.pdf

static/  (CSS, шрифты, favicon, фото) ──► копируется в public/ как есть
```

Одни и те же данные превращаются в HTML **и** в PDF двумя независимыми
шаблонизаторами (Jinja2 для HTML, встроенный `yaml()` Typst для PDF) — так
дизайн сайта и PDF синхронны по контенту, при этом каждый файл верстается
инструментом, для этого предназначенным.

---

## Структура репозитория

```
data/
  resume.ru.yaml        — контент, русская версия
  resume.en.yaml        — контент, английская версия (та же схема полей)

templates/
  index.html.j2         — HTML-шаблон (Jinja2). Структура страницы, не контент.

resume.typ               — PDF-шаблон (Typst). Читает data/resume.<lang>.yaml
                            напрямую через yaml(), контент не дублирует.

static/
  style.css              — вся дизайн-система сайта (цвета, шрифты, раскладка)
  print.css               — стили для печати страницы через Ctrl+P
  assets/
    favicon.svg            — иконка вкладки
    photo.jpg               — твоё фото (опционально, см. ниже)
    og-image.png            — превью для соцсетей/мессенджеров (генерируется, см. ниже)
    fonts/                  — .ttf-файлы шрифтов (нужны Typst для PDF, см. ниже)

build.py                 — собирает HTML: data/*.yaml + templates/ → public/
generate_og_image.py     — рисует static/assets/og-image.png из resume.ru.yaml
requirements.txt         — Python-зависимости (Jinja2, PyYAML, Pillow)

.github/workflows/deploy.yml — CI: при push в main собирает HTML+PDF+og-image
                                 и публикует на GitHub Pages

public/                  — СГЕНЕРИРОВАННЫЙ результат сборки. В .gitignore,
                            руками не редактируется — любые правки исчезнут
                            при следующей сборке.
```

---

## Как редактировать контент

### Текст, опыт, скиллы, контакты
Правь **только** `data/resume.ru.yaml` и `data/resume.en.yaml` — не HTML, не
`resume.typ`. Оба файла должны иметь одинаковый набор ключей (одинаковую
структуру), отличаться только значениями на разных языках.

Схема полей (одинакова в обоих файлах):

| Поле | Что это | Обязательно |
|---|---|---|
| `name` | Имя | да |
| `photo` | Путь к фото для **HTML**, от `static/` (напр. `assets/photo.jpg`) | нет — пусто = блок с фото не рендерится |
| `photo_pdf` | Путь к фото для **PDF**, от корня репозитория (напр. `static/assets/photo.jpg`) | нет |
| `role`, `tagline` | Роль и подзаголовок под именем | да |
| `summary` | Абзац "о себе" | да |
| `contacts.*` | email, telegram, github, linkedin, location | email/location да, остальное можно пусто |
| `portfolio_url` | Ссылка на отдельный проект-портфолио | нет — пусто = кнопка не рендерится |
| `resume_pdf` | Имя PDF-файла для этого языка | да, **и обязательно разное** для ru/en (см. «Частые ошибки») |
| `skills` | Список групп: `group` (название) + `tags` (список технологий) | да |
| `experience` | Список мест работы: `company`, `role`, `period`, `bullets` (список строк) | да |
| `projects` | Список проектов: `name`, `url`, `description` | нет — пусто = секция не рендерится |
| `education` | Список: `org`, `url` (необязательно), `degree`, `detail`, `period` | да |
| `footer_note` | Строка в подвале страницы | да |

### Добавить новую запись в существующий список
Просто допиши элемент в массив в обоих yaml-файлах. Например, новое место работы:

```yaml
experience:
  - company: "Новая компания"
    role: "..."
    period: "2026 — н.в."
    bullets:
      - "Что делал"
  - company: "Старая компания"   # была тут и раньше
    ...
```
Порядок в списке = порядок вывода на странице. Пересобери (`python build.py`) — появится само, без правки HTML/Typst.

### Добавить новую ссылку/проект
```yaml
projects:
  - name: "Третий проект"
    url: "https://github.com/you/project3"
    description: "Что он делает"
```

---

## Как добавить целиком новый раздел (пример: "Сертификаты")

Раздела в схеме нет — потребуется правка в 4 местах. Пример добавления
раздела `certificates`:

**1. `data/resume.ru.yaml` и `data/resume.en.yaml`** — добавь данные:
```yaml
certificates:
  - name: "AWS Certified SysOps Administrator"
    year: "2025"
```

**2. `templates/index.html.j2`** — добавь секцию (скопируй по образцу Projects):
```html
{% if certificates %}
<section class="section">
  <h2 class="section__title">{{ t.certificates }}</h2>
  <ul class="projects">
    {% for c in certificates %}
    <li class="project"><h3>{{ c.name }}</h3><p class="muted">{{ c.year }}</p></li>
    {% endfor %}
  </ul>
</section>
{% endif %}
```

**3. `build.py`** — добавь заголовок раздела в оба языка `UI_STRINGS`:
```python
UI_STRINGS = {
    "ru": {..., "certificates": "Сертификаты"},
    "en": {..., "certificates": "Certificates"},
}
```

**4. `resume.typ`** — добавь заголовок в словарь `ui` и вывод по образцу Projects:
```typst
#let ui = (
  ru: (..., certificates: "Сертификаты"),
  en: (..., certificates: "Certificates"),
)
```
```typst
#if "certificates" in data.keys() [
  #section[#t.certificates]
  #for c in data.certificates [
    *#c.name* --- #c.year
  ]
]
```

Пересобери и проверь (см. «Как собрать и проверить локально»).

## Как убрать раздел
Обратная операция: убери секцию из `index.html.j2` (или оберни в
`{% if false %}`, если хочешь временно скрыть, не удаляя код), убери блок из
`resume.typ`, оставь данные в yaml нетронутыми (не используются — не рендерятся,
это не ошибка).

---

## Фото

1. Положи квадратное фото (от 300×300px) в `static/assets/photo.jpg`
2. В **обоих** `resume.*.yaml`:
   ```yaml
   photo: "assets/photo.jpg"           # для HTML
   photo_pdf: "static/assets/photo.jpg" # для PDF — путь от корня репозитория
   ```
3. На сайте оно автоматически идёт в градациях серого (см. `.hero__photo` в
   `style.css`, `filter: grayscale(1)`) — убери строку `filter`, если хочешь
   цветное. В PDF цветное всегда (Typst не умеет CSS-фильтры).

---

## Языки (RU/EN)

Переключатель наверху страницы (`RU · EN`) ведёт на `/` и `/en/` —
это две независимые статические страницы, не JS-переключение.

**Как это работает:**
- `build.py` рендерит `templates/index.html.j2` дважды — с данными из
  `resume.ru.yaml` в `public/index.html`, и из `resume.en.yaml` в
  `public/en/index.html`
- `resume.typ` компилируется дважды с флагом `--input lang=ru` / `--input lang=en`
  (см. `.github/workflows/deploy.yml`, шаг «Compile PDFs»), выбирая нужный
  yaml через `sys.inputs.at("lang", ...)`
- Текст интерфейса (заголовки разделов, подписи кнопок — не личные данные)
  вынесен отдельно: `UI_STRINGS` в `build.py` для HTML, словарь `ui` в
  `resume.typ` для PDF. Личные данные (имя, опыт) — только в `resume.*.yaml`.

**Добавить третий язык** (например, немецкий):
1. Создай `data/resume.de.yaml` по образцу существующих
2. В `build.py`: добавь ключ `"de"` в `UI_STRINGS` и в `LOCALES`
   (`out_path` → `public/de/index.html`, свой `og_locale`)
3. В `resume.typ`: добавь ключ `de` в словарь `ui`
4. В `.github/workflows/deploy.yml`: добавь `de` в `for LANG in ru en de`
5. В `templates/index.html.j2`: добавь ссылку `<a href="/de/">DE</a>` в блок
   `.lang-switch`

### Частые ошибки с языками
- **`resume_pdf` совпадает в ru и en** → один язык при сборке молча
  перезаписывает PDF другого, обе кнопки в итоге ведут на один и тот же
  (последний собранный) файл. `build.py` теперь проверяет это сам и
  падает с понятным сообщением, если имена совпали — если увидел такую
  ошибку при сборке, просто дай файлам разные имена.
- Отредактировал только `resume.ru.yaml`, забыл про `resume.en.yaml` →
  английская версия отстаёт по контенту. Оба файла редактируются вручную,
  синхронизация не автоматическая (это не перевод-бот, а два файла с
  одинаковой структурой) — веди привычку менять оба сразу.

---

## Как собрать и проверить локально

```bash
# HTML
python build.py
python -m http.server -d public 8080   # http://localhost:8080 (RU), /en/ (EN)

# PDF (нужен установленный typst: https://github.com/typst/typst/releases)
typst compile resume.typ public/resume_ru.pdf --font-path static/assets/fonts
typst compile resume.typ public/resume_en.pdf --font-path static/assets/fonts --input lang=en

# og-image.png (нужны шрифты в static/assets/fonts/, см. ниже)
python generate_og_image.py
```

## Шрифты для PDF/og-image

Typst и Pillow не видят системные шрифты Google Fonts — нужны файлы `.ttf`,
закоммиченные в `static/assets/fonts/`:
- `SourceSerif4-SemiBold.ttf` — https://fonts.google.com/specimen/Source+Serif+4
- `JetBrainsMono-Medium.ttf` — https://fonts.google.com/specimen/JetBrains+Mono

Скачай через кнопку **Get font → Download all**, файлы лежат в `static/` внутри
архива. Без них Typst выдаст `warning: unknown font family` и молча
подставит системный шрифт — сайт и PDF разъедутся визуально.

---

## Дизайн-система

Все цвета/шрифты/отступы — в `:root` в начале `static/style.css`, продублированы
как явные `rgb(...)` в начале `resume.typ` (Typst не читает CSS-файлы, поэтому
токены руками синхронизированы в двух местах — при смене палитры правь оба).

Тема: светлый/тёмный автоматически по `prefers-color-scheme` в браузере;
PDF — всегда светлый (тёмный фон в PDF плохо ведёт себя при печати и в ATS).

---

## Что можно / нельзя делать руками

**Можно и нужно:** редактировать `data/resume.ru.yaml` и `resume.en.yaml` —
это единственные файлы, которые правишь при обновлении резюме.

**Можно, но осторожно:** менять `static/style.css` (визуал),
`templates/index.html.j2` и `resume.typ` (структура/новые разделы) —
см. «Как добавить новый раздел» выше, правь оба шаблона синхронно.

**Нельзя:** редактировать `public/` — это сгенерированный результат, всё
затрётся следующей сборкой. Если увидел ошибку на сайте — ищи причину в
`data/*.yaml` или `templates/`, не в `public/`.

---

## CI/CD

`.github/workflows/deploy.yml` при каждом push в `main`:
1. Генерирует `og-image.png` (`generate_og_image.py`)
2. Собирает оба HTML (`build.py`)
3. Компилирует оба PDF (`resume.typ` × 2, с `--input lang=`)
4. Публикует `public/` на GitHub Pages

Прогресс — во вкладке **Actions** репозитория. Красный крест на шаге — открой
его, там точный текст ошибки Python/Typst, не только "exit code 1".