# Domain Model Assistant

> An AI-powered web application that lets domain experts create, version, and evolve database schemas through natural language — no SQL knowledge required.

---

## What is this?

Domain Model Assistant bridges the gap between business requirements and software database design. Using LLM agents, it translates plain English instructions into versioned SQLite schemas, generates ER diagrams, auto-writes test suites, and lets users safely run and validate queries — all from a browser.

---

## Features

- **Natural language schema generation** — describe your domain in plain English; get a valid SQL schema + Mermaid ER diagram
- **SQL upload support** — import existing `.sql` files; the system normalizes dialect, generates diagrams and tests automatically
- **Versioned schemas** — every change creates a new immutable version; nothing is ever overwritten in place
- **AI-generated test suites** — at least 5 normal + 5 edge-case tests generated per version
- **Safe SQL sandbox** — queries run inside SAVEPOINTs and are rolled back unless explicitly committed
- **Schema editor agent** — request modifications in plain English; edits are applied as a new version
- **Static analysis** — SQLGlot checks for missing PKs, invalid FKs, and naming convention issues
- **Utility documentation** — auto-generated human-readable table/column purpose descriptions
- **Per-user isolation** — each user's projects and version DBs are fully sandboxed

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ORM / Auth DB | SQLAlchemy + SQLite (`app.db`) |
| Per-version DB | SQLite (one file per version) |
| LLM Agents | Pluggable LLM API (OpenAI-compatible) |
| Static Analysis | `sqlglot` |
| Frontend | Jinja2 templates |
| Diagrams | Mermaid.js |
| Password hashing | Werkzeug |

---

## Project Structure

```
project-root/
├── app.py                  # Flask application, routes, agent calls
├── app.db                  # SQLAlchemy system database (users, projects, versions)
├── userdata/
│   └── {user_id}/
│       └── project_{id}/
│           └── version{n}/
│               ├── schema.sql        # Canonical SQL schema
│               ├── backend.db        # Per-version SQLite DB
│               ├── test_suite.json   # AI-generated tests
│               ├── utility.md        # Business-purpose documentation
│               └── mermaid.md        # ER diagram source
├── templates/              # Jinja2 HTML templates
└── static/                 # CSS, JS assets
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
git clone https://github.com/your-org/domain-model-assistant.git
cd domain-model-assistant
pip install -r requirements.txt
```

### Configuration

Set your LLM API key in the environment (or a `.env` file):

```bash
export OPENAI_API_KEY=sk-...
export SECRET_KEY=your-flask-secret-key
```

### Run

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

---

## Usage

1. **Register / Login** at the splash screen
2. **Create a project** from the dashboard
3. **Create version 1** — either type a business description or upload a `.sql` file
4. In the **version workspace**:
   - View the generated schema and Mermaid ER diagram
   - Run individual SQL queries (reads or sandboxed writes)
   - Run the full AI-generated test suite
   - Request schema modifications in plain English → creates a new version automatically
5. Compare versions and promote when ready

---

## LLM Agents

| Agent | Input | Output |
|---|---|---|
| Generator | Business prompt | SQL schema + Mermaid ER |
| Diagram | Existing SQL | Mermaid ER only |
| Test Suite | SQL schema | JSON array of normal + edge tests |
| Editor | Schema + instruction | JSON diff (modify / add / remove tables) |

---

## Known Limitations

- Only SQLite dialect is supported for per-version DBs (MySQL schemas are auto-normalized on import)
- Agent pipeline is single-pass; fully autonomous iterative refinement is planned but not yet implemented
- No approval/diff UI between versions yet (planned)

---

## Roadmap

- [ ] Side-by-side version diff UI
- [ ] Approval workflow with reviewer comments
- [ ] Autonomous editor-validator agent loop
- [ ] ZIP export (schema + tests + docs)
- [ ] CSRF protection and session hardening
- [ ] Rate limiting on LLM calls per user

---

## License

MIT License. See `LICENSE` for details.
