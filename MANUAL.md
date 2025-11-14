# Project Manual

This manual documents the application features, scripts, structure, and how to run everything locally on Windows or WSL.

## Contents
- Scripts
- Python package (consulting)
- Web pages
- Setup and running
- Documentation policy

## Scripts

### business_analyzer.py
- Purpose: Interactive CLI to collect basic business info and produce a JSON file and a short text report.
- Prompts for: name, industry, employees, revenue, up to 3 challenges.
- Outputs:
  - <business> .json
  - <business> _report.txt
- Error handling: Robust try/except at entrypoint; writes tracebacks to stderr on fatal errors.
- Run:
  - PowerShell (Windows): `python business_analyzer.py`
  - WSL: `python3 /mnt/c/Users/lindj/consulting-projects/My\ First\ Repo/my-first-repo/business_analyzer.py`

### report_generator.py
- Purpose: Generate a Markdown consulting report from a JSON file.
- Required sections included in output: Executive Summary, Current State Analysis, Key Findings, Recommendations, Next Steps.
- Optional JSON fields: `executive_summary`, `current_state`, `findings[]`, `recommendations[]`, `next_steps[]`, `challenges[]`.
- Output filename: `<business_name>_consulting_report.md` (falls back to input filename stem).
- Error handling: Validates file existence and JSON structure; robust try/except at entrypoint.
- Run:
  - PowerShell (Windows): `python report_generator.py sample_business.json`
  - WSL: `python3 /mnt/c/Users/lindj/consulting-projects/My\ First\ Repo/my-first-repo/report_generator.py /mnt/c/Users/lindj/consulting-projects/My\ First\ Repo/my-first-repo/sample_business.json`

#### Sample JSON
- File: `sample_business.json` (included) demonstrates supported fields.

### client_intake.py
- Purpose: Minimal command-line intake to collect basic client and business info, saving to JSON.
- Fields collected: `name`, `email`, `phone` (optional), `business_name`, `employees_count`, `industry`, `main_challenge`.
- Validation: Practical email regex; non-negative integer for employees (commas allowed).
- Output: `<business_name>_<name>.json` (sanitized filename) in the current folder.
- Run:
  - PowerShell (Windows): `python client_intake.py`

## Python package: consulting

Module providing shared utilities and report builders.

- consulting/__init__.py
  - Re-exports common functions/constants for convenience.
- consulting/config.py
  - `DEFAULT_ENCODING = "utf-8"`
  - `REPORT_TITLE_PREFIX = "Jared Consulting — "`
- consulting/data_processing.py
  - `read_json(path: Path) -> dict`: Load and validate JSON.
  - `sanitize_filename(name: str) -> str`: Safe filename base.
- consulting/analysis.py
  - `build_summary(data: dict) -> str`: Console-friendly summary of inputs.
- consulting/reporting.py
  - `format_currency(value) -> str`
  - `list_block(items: list[str]) -> str`
  - `build_report_text(data: dict) -> str`: Plain text report body.
  - `build_markdown(data: dict) -> str`: Full Markdown report with required sections.

## Web pages

### index.html
- One-page consulting site with hero, services, and contact form.
- Design: Modern blue/white palette; responsive.
- JS: `script.js` for nav toggle, form validation, and footer year.

### client_interview_generator.html
- Generates 10–15 interview questions from inputs:
  - Business type, Company size, Focus area.
- Features: Copy-to-clipboard, Back to site button, modern styling using primary blue `#2563eb`.

## Setup and running

### View the website
- Open `index.html` directly in a browser.
- Optional local server:
  - Python 3: `python -m http.server 5500` then visit http://localhost:5500

### Run Python scripts
- PowerShell (recommended):
  - `python business_analyzer.py`
  - `python report_generator.py sample_business.json`
- WSL:
  - Use full `/mnt/c/...` paths as shown above.

## Documentation policy
- Any code change must be reflected in this MANUAL.md.
- Include: purpose, how to run, inputs/outputs, and any new configuration.
- Keep README.md concise; use this manual for detailed instructions.

## Testing

- Framework: pytest
- Install (PowerShell/WSL):
  - `pip install pytest`
- Run all tests from repo root:
  - `pytest -q`
- Tests included:
  - `tests/test_business_analyzer.py` covering input parsing, confirmation flow, and file creation.
