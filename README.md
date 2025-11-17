# my-first-repo
Learning GitHub basics
## Skills I'm Learning
- Git and GitHub
- AI-assisted development
- Business consulting
- 

## Installation

- Open `index.html` directly in your web browser (no build step required).
- Or serve the folder locally for a better dev experience:
  - Python 3: `python -m http.server 5500`
  - Node (serve): `npx serve`
  - Then visit `http://localhost:5500` (or the URL shown by the server).
- Edit site files:
  - `index.html`
  - `styles.css`
  - `script.js`

## Usage

### Website pages
- `index.html` — Main consulting site (Hero, Services, Contact). Nav includes links to Questions and Projects.
- `contact.html` — Standalone contact page with validation and animated success message.
- `client_interview_generator.html` — Generates 10–15 tailored interview questions; includes copy-to-clipboard and back-to-site link.
- `projects.html` — Vanilla JavaScript SPA for projects (Dashboard, List, Detail, Form) using localStorage.
- `projects-react.html` — React-based SPA that mirrors the vanilla app and reuses the same localStorage key (data carries over).

Open any of the above directly in a browser. No build step required.

### Python scripts
- `business_analyzer.py`
  - Interactive prompts: business name, industry, employees, revenue, up to 3 challenges.
  - Creates `<Business>.json` and `<Business>_report.txt`.
  - Run (PowerShell): `python business_analyzer.py`
- `report_generator.py`
  - Generates a Markdown consulting report from JSON.
  - Sample: `sample_business.json`
  - Run (PowerShell): `python report_generator.py sample_business.json`

### Tests
- Uses `pytest`.
- Install: `pip install pytest`
- Run from repo root: `pytest -q`

## Configuration

- Python config: `consulting/config.py`
  - `DEFAULT_ENCODING` — File encoding for JSON/markdown IO.
  - `REPORT_TITLE_PREFIX` — Prefix used in generated reports.
- Projects apps (vanilla + React)
  - LocalStorage key: `jc_projects_v1` (shared so both apps see the same data).
- Styling
  - Primary blue: `#2563eb` (see `styles.css`, `projects.css`).

## Troubleshooting

- Running Python from the wrong directory
  - Symptom: `can't open file 'C:\\WINDOWS\\system32\\...py'`
  - Fix: Open PowerShell in the project folder (right-click folder → Open in Terminal) or use full paths.

- `py` not found in WSL
  - Use `python3` in WSL or run `python` in Windows PowerShell.

- WSL path issues
  - Use absolute paths like `/mnt/c/Users/.../my-first-repo/...` when invoking from WSL.

- LocalStorage data not persisting
  - Incognito/private windows may clear storage on close. Use a normal tab or export/import data manually if needed.

- React UMD page fails offline
  - `projects-react.html` loads React from a CDN. Ensure you’re online or migrate to a build setup (Vite) to bundle locally.

- Clipboard permissions in the question generator
  - If the browser blocks clipboard access, the app falls back to a hidden textarea copy method.