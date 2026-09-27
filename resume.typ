// resume.typ — PDF-версия резюме.
// Контент НЕ дублируется руками: yaml() читает data/resume.yaml прямо во время
// компиляции. Меняешь только resume.yaml — PDF и HTML всегда синхронны.
// Тут только вёрстка/дизайн (цвета/шрифты/раскладка) — тот же язык, что в style.css.
//
// Компиляция (см. .github/workflows/deploy.yml):
//   typst compile resume.typ public/resume_mansimovrr.pdf --font-path static/assets/fonts

// Язык передаётся флагом компиляции: typst compile resume.typ out.pdf --input lang=en
// По умолчанию (если флаг не передан) — русский.
#let lang = sys.inputs.at("lang", default: "ru")
#let data = yaml("data/resume." + lang + ".yaml")

// Заголовки разделов — та же логика "UI-строки отдельно от данных", что в build.py
#let ui = (
  ru: (about: "Обо мне", skills: "Стек", experience: "Опыт", projects: "Проекты", education: "Образование", contacts: "Контакты"),
  en: (about: "About", skills: "Stack", experience: "Experience", projects: "Projects", education: "Education", contacts: "Contacts"),
)
#let t = ui.at(lang)

// Светлая тема — те же значения, что в static/style.css под
// @media (prefers-color-scheme: light), чтобы PDF не расходился с сайтом
// и был пригоден для печати/ATS-сканирования (тёмный фон в PDF — плохая
// практика: жрёт тонер при печати и часто ломает извлечение текста ATS)
#set page(margin: 2cm, fill: rgb("#f6f5f2"))
#set text(font: "Source Serif 4", size: 10.5pt, fill: rgb("#17181b"))

#let fg = rgb("#17181b")
#let accent = rgb("#9c6f00")
#let muted = rgb("#6b6a66")
#let border = rgb("#dedcd6")

// mono() — обёртка для мета-данных (даты/лейблы), как .hero__role/.tag в CSS
#let mono(body) = text(font: "JetBrains Mono", size: 8.5pt, fill: muted, body)

// section() — заголовок раздела с левой акцентной чертой, как .section__title
#let section(title) = {
  v(0.4cm)
  box(inset: (left: 0.3cm), stroke: (left: 2pt + accent))[
    #text(size: 13pt, weight: "semibold", fill: fg)[#title]
  ]
  v(0.3cm)
}

// ---- PHOTO (опционально) -----------------------------------------------
// #place кладёт элемент абсолютно поверх текущего потока — не сдвигает
// остальной контент, в отличие от обычной вставки image()
#if "photo_pdf" in data.keys() and data.photo_pdf != "" [
  #place(top + right, dx: 0pt, dy: 0pt)[
    #box(
      width: 2.2cm, height: 2.2cm,
      clip: true,
      stroke: 0.5pt + border,
    )[#image(data.photo_pdf, width: 2.2cm, height: 2.2cm, fit: "cover")]
  ]
]

// ---- HERO -------------------------------------------------------------
#text(size: 26pt, weight: "semibold", fill: fg)[#data.name]
#v(0.15cm)
#mono[#data.role]
#v(0.1cm)
#text(fill: muted, size: 9.5pt)[#data.tagline]

#v(0.3cm)
#line(length: 100%, stroke: 0.5pt + border)

// ---- ABOUT --------------------------------------------------------------
#section[#t.about]
#data.summary

// ---- SKILLS ---------------------------------------------------------------
#section[#t.skills]
#for block in data.skills [
  #mono[#block.group]  #block.tags.join(" · ")  \
  #v(0.15cm)
]

// ---- EXPERIENCE -----------------------------------------------------------
#section[#t.experience]
#for job in data.experience [
  *#job.role* --- #job.company #h(1fr) #mono[#job.period]
  #for b in job.bullets [
    - #b
  ]
  #v(0.25cm)
]

// ---- PROJECTS ---------------------------------------------------------------
#if "projects" in data.keys() [
  #section[#t.projects]
  #for p in data.projects [
    *#link(p.url)[#p.name]*
    #text(fill: muted, size: 9pt)[#p.description]
    #v(0.2cm)
  ]
]

// ---- EDUCATION --------------------------------------------------------------
#section[#t.education]
#for ed in data.education [
  #if "url" in ed.keys() [
    *#link(ed.url)[#ed.org]*
  ] else [
    *#ed.org*
  ]
  #h(1fr) #mono[#ed.period]

  #ed.degree
  #if ed.detail != "" [
    #text(fill: muted, size: 9pt)[#ed.detail]
  ]
  #v(0.25cm)
]

// ---- CONTACTS ---------------------------------------------------------------
#section[#t.contacts]
#mono[email] #data.contacts.email #h(1fr) #mono[location] #data.contacts.location \
#if data.contacts.github != "" [#mono[github] #data.contacts.github]
