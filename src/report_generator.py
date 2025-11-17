import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


TEMPLATE_SUBPATH = os.path.join("templates", "report-template.md")


@dataclass
class ClientContext:
    business_name: str
    industry: str
    employees: int
    contact_name: str
    email: str
    phone: str
    main_challenge: str
    challenges_raw: Any
    extra: Dict[str, Any]


def load_client_json(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Client JSON not found: {p}")
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:  # noqa: TRY003
        raise ValueError(f"Invalid JSON file: {p}\n{exc}") from exc


def build_context(data: Dict[str, Any]) -> ClientContext:
    business_name = (
        data.get("business_name")
        or data.get("name")
        or data.get("business")
        or "Client"
    )
    industry = data.get("industry") or "N/A"
    employees = (
        data.get("employees")
        or data.get("employees_count")
        or data.get("num_employees")
        or 0
    )
    try:
        employees = int(employees)
    except (TypeError, ValueError):
        employees = 0

    contact_name = data.get("name") or data.get("owner_name") or "N/A"
    email = data.get("email") or "N/A"
    phone = data.get("phone") or "N/A"

    # Challenges can appear in multiple shapes
    challenges_raw: Any = (
        data.get("challenges")
        or data.get("main_challenges")
        or [data.get("main_challenge")] if data.get("main_challenge") else []
    )

    main_challenge = ""
    if isinstance(challenges_raw, list) and challenges_raw:
        main_challenge = str(challenges_raw[0])
    elif isinstance(challenges_raw, str):
        main_challenge = challenges_raw

    extra = {k: v for k, v in data.items() if k not in {
        "business_name",
        "name",
        "business",
        "industry",
        "employees",
        "employees_count",
        "num_employees",
        "email",
        "phone",
        "main_challenge",
        "main_challenges",
        "challenges",
    }}

    return ClientContext(
        business_name=business_name,
        industry=industry,
        employees=employees,
        contact_name=contact_name,
        email=email,
        phone=phone,
        main_challenge=main_challenge,
        challenges_raw=challenges_raw,
        extra=extra,
    )


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in value)
    while "--" in value:
        value = value.replace("--", "-")
    value = value.strip("-_")
    return value or "client"


def load_template(base_dir: Path, template_path: Optional[str] = None) -> str:
    if template_path is None:
        template_path = TEMPLATE_SUBPATH
    p = base_dir / template_path
    if not p.is_file():
        raise FileNotFoundError(f"Report template not found: {p}")
    return p.read_text(encoding="utf-8")


def render_analysis(ctx: ClientContext) -> Dict[str, str]:
    # 1) Business profile summary
    profile_parts = [
        f"{ctx.business_name} operates in the {ctx.industry} space.",
    ]
    if ctx.employees > 0:
        size = "small" if ctx.employees <= 25 else "mid-sized" if ctx.employees <= 250 else "large"
        profile_parts.append(
            f"The organization is a {size} team with approximately {ctx.employees} employees."
        )

    business_profile_summary = " " .join(profile_parts)

    # 2) Key metrics interpretation (basic heuristic)
    metrics_lines: list[str] = []
    if ctx.employees > 0:
        if ctx.employees <= 10:
            metrics_lines.append(
                "Headcount suggests a lean operation; capacity and owner dependency are likely key risks."
            )
        elif ctx.employees <= 50:
            metrics_lines.append(
                "Headcount indicates a growing team; process standardization and role clarity become important."
            )
        else:
            metrics_lines.append(
                "Headcount points to a larger organization where cross-functional coordination and governance matter."
            )
    if isinstance(ctx.extra.get("annual_revenue"), (int, float)):
        revenue = ctx.extra["annual_revenue"]
        if revenue < 250_000:
            metrics_lines.append(
                "Revenue is in an early-stage band; improving lead generation and offer clarity is often highest impact."
            )
        elif revenue < 1_000_000:
            metrics_lines.append(
                "Revenue suggests product–market fit; focus often shifts to scalable delivery and customer retention."
            )
        else:
            metrics_lines.append(
                "Revenue indicates established traction; systematizing operations and leadership depth become priorities."
            )

    metrics_interpretation = "\n\n".join(metrics_lines) or (
        "Based on the available data, the business appears to be in a growth phase. "
        "Further quantitative metrics (margin, conversion, retention) would enable a deeper analysis."
    )

    # 3) Challenge prioritization
    challenges: list[str] = []
    if isinstance(ctx.challenges_raw, list):
        challenges = [str(c) for c in ctx.challenges_raw if c]
    elif isinstance(ctx.challenges_raw, str) and ctx.challenges_raw.strip():
        challenges = [ctx.challenges_raw.strip()]

    if not challenges and ctx.main_challenge:
        challenges = [ctx.main_challenge]

    challenge_list_md = "\n".join(f"- {c}" for c in challenges) or "- Not explicitly stated."

    if challenges:
        top = challenges[0]
        prioritization = (
            f"The primary stated challenge is **{top}**. Secondary or related challenges "
            "should be clarified in follow-up discussions to confirm priorities."
        )
    else:
        prioritization = (
            "No explicit challenges were captured. A short discovery conversation is recommended to "
            "clarify the top 2–3 problems before prescribing solutions."
        )

    # 4) Quick wins
    quick_wins_lines: list[str] = []
    ch_text = " ".join(challenges).lower()
    if "sales" in ch_text or "lead" in ch_text:
        quick_wins_lines.append(
            "- Clarify a single core offer and tighten the ideal customer profile for the next 90 days."
        )
        quick_wins_lines.append(
            "- Standardize a simple follow-up sequence for all open quotes and past leads."
        )
    if "operations" in ch_text or "process" in ch_text or "delivery" in ch_text:
        quick_wins_lines.append(
            "- Map the top 3 recurring processes and introduce simple checklists to reduce errors."
        )
    if "cash" in ch_text or "profit" in ch_text or "margin" in ch_text:
        quick_wins_lines.append(
            "- Review pricing and discounting rules on the last 3 months of deals to identify quick margin gains."
        )
    if not quick_wins_lines:
        quick_wins_lines.append(
            "- Book a 60-minute working session to clarify goals, constraints, and quick-win opportunities."
        )

    quick_wins = "\n".join(quick_wins_lines)

    # 5) Focus areas
    focus_lines: list[str] = []
    if "roof" in ctx.industry.lower():
        focus_lines.append(
            "- Build a simple, repeatable sales process from first contact through signed contract and install."
        )
        focus_lines.append(
            "- Implement basic job cost tracking per project to understand true profitability by job type."
        )
    if ctx.employees >= 5:
        focus_lines.append(
            "- Clarify roles and handoffs between sales, operations, and admin to reduce owner bottlenecks."
        )
    if not focus_lines:
        focus_lines.append(
            "- Define 3 measurable outcomes for the next 6 months and align projects directly to these outcomes."
        )

    focus_areas = "\n".join(focus_lines)

    return {
        "BUSINESS_PROFILE_SUMMARY": business_profile_summary,
        "METRICS_INTERPRETATION": metrics_interpretation,
        "CHALLENGE_LIST": challenge_list_md,
        "CHALLENGE_PRIORITIZATION": prioritization,
        "QUICK_WINS": quick_wins,
        "FOCUS_AREAS": focus_areas,
        "NEXT_STEPS": "Schedule a follow-up session to validate assumptions and finalize the 90-day plan.",
    }


def fill_template(template: str, ctx: ClientContext, analysis: Dict[str, str]) -> str:
    # Simple {{ PLACEHOLDER }} replacement. We keep it intentionally minimal.
    replacements = {
        "BUSINESS_NAME": ctx.business_name,
        "INDUSTRY": ctx.industry,
        "EMPLOYEES": str(ctx.employees) if ctx.employees else "Not specified",
        "CONTACT_NAME": ctx.contact_name,
        "EMAIL": ctx.email,
        "PHONE": ctx.phone,
        "LOCATION": ctx.extra.get("location", "Not specified"),
        "OFFERING": ctx.extra.get("offering", "Not specified"),
        "EXECUTIVE_SUMMARY": ctx.extra.get(
            "executive_summary",
            "This report summarizes the current state, challenges, and opportunities for the business.",
        ),
    }
    replacements.update(analysis)

    result = template
    for key, value in replacements.items():
        result = result.replace(f"{{{{ {key} }}}}", str(value))
    return result


def save_report(base_dir: Path, ctx: ClientContext, content: str) -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(ctx.business_name)
    rel_dir = Path("data") / "reports"
    out_dir = base_dir / rel_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{slug}-report-{date_str}.md"
    out_path = out_dir / filename
    out_path.write_text(content, encoding="utf-8")
    return out_path


def generate_report(client_json_path: str, base_dir: Optional[str] = None, template_path: Optional[str] = None) -> Path:
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base = Path(base_dir)

    data = load_client_json(client_json_path)
    ctx = build_context(data)
    template = load_template(base, template_path)
    analysis = render_analysis(ctx)
    content = fill_template(template, ctx, analysis)
    return save_report(base, ctx, content)


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Generate a consulting report from client JSON data.")
    parser.add_argument("client_json", help="Path to the client JSON file.")
    parser.add_argument(
        "--template",
        dest="template",
        default=None,
        help="Optional path to a custom Markdown template (relative to project root or absolute).",
    )
    args = parser.parse_args(argv)

    try:
        report_path = generate_report(args.client_json, template_path=args.template)
    except Exception as exc:  # noqa: BLE001
        print(f"Error generating report: {exc}")
        raise SystemExit(1) from exc

    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    main()
