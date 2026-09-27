// resume.typ — компилируется в PDF: typst compile resume.typ static/resume.pdf
// Контент сейчас продублирован вручную из data/resume.yaml.
// Если резюме будет часто меняться — вынеси текст в resume.yaml и генерируй
// этот файл через build.py тем же способом, что и index.html (см. README, шаг «Автоматизация PDF»).

#set page(margin: 2cm, fill: rgb("#0f1013"))
#set text(font: "Source Serif 4", size: 10.5pt, fill: rgb("#e7e4dd"))

#let accent = rgb("#c9972f")
#let muted = rgb("#8b8a86")

#let mono(body) = text(font: "JetBrains Mono", size: 8.5pt, fill: muted, body)

= #text(fill: white)[Руслан ...]
#mono[DevOps / SRE Engineer]

#v(0.3cm)
#line(length: 100%, stroke: 0.5pt + rgb("#2a2a2b"))
#v(0.3cm)

DevOps/SRE и сетевой инженер в fintech-компании, эксплуатирующей платёжный шлюз
в контуре PCI DSS. Отвечаю за инфраструктуру ~14 dev-серверов: виртуализацию,
CI/CD, сетевую безопасность и мониторинг.

== #text(fill: accent)[Стек]

#mono[OS & Virtualization] — Rocky Linux, QEMU/KVM, Docker, Kubernetes \
#mono[Automation & CI/CD] — Ansible, GitLab CI/CD, Terraform, Python \
#mono[Security & Networking] — nftables, strongSwan, HashiCorp Vault, mod_security, PCI DSS \
#mono[Data & Messaging] — Oracle 19c, PostgreSQL 18, RabbitMQ, Kafka, Ceph \
#mono[Observability] — Zabbix, Prometheus, Grafana, Telegraf, InfluxDB v2

== #text(fill: accent)[Опыт]

*DevOps / SRE Engineer* — Название компании #h(1fr) #mono[20XX — н.в.]
- Администрирование ~14 dev-серверов на Rocky Linux в контуре PCI DSS
- Построение и поддержка CI/CD пайплайнов на GitLab CI
- Внедрение HashiCorp Vault для управления секретами

== #text(fill: accent)[Образование]

*СПбГУТ им. проф. М. А. Бонч-Бруевича* #h(1fr) #mono[2026 — н.в.]
Магистратура, 11.04.02 ИКТиСС, профиль: ML/DL для тактильного интернета и метавселенных

== #text(fill: accent)[Контакты]

#mono[email] your@email.com  #h(1fr)  #mono[github] github.com/your-username
