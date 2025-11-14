from typing import Any, Dict, List

from .config import REPORT_TITLE_PREFIX


def format_currency(value: Any) -> str:
    try:
        v = float(value)
        return f"${v:,.2f}"
    except Exception:
        return str(value)


def list_block(items: List[str]) -> str:
    if not items:
        return "- (none provided)"
    return "\n".join(f"- {x}" for x in items)


def build_report_text(data: Dict[str, Any]) -> str:
    challenges = data.get("challenges", []) or []
    ch_block = "\n".join([f"- {c}" for c in challenges]) if challenges else "- None provided"
    return (
        f"{REPORT_TITLE_PREFIX}Business Analysis\n"
        "====================================\n\n"
        "Business Profile\n"
        "----------------\n"
        f"- Name: {data.get('business_name', '(Unnamed)')}\n"
        f"- Industry: {data.get('industry', '(unspecified)')}\n"
        f"- Employees: {data.get('employees', '(unspecified)')}\n\n"
        "Key Metrics\n"
        "-----------\n"
        f"- Annual Revenue: {format_currency(data.get('annual_revenue'))}\n\n"
        "Challenges to Address\n"
        "---------------------\n"
        f"{ch_block}\n"
    )


def build_markdown(data: Dict[str, Any]) -> str:
    name = str(data.get("business_name") or data.get("name") or "(Unnamed Business)")
    industry = str(data.get("industry") or "(unspecified)")
    employees = data.get("employees")
    revenue = data.get("annual_revenue")
    challenges = data.get("challenges") or []

    executive_summary = data.get("executive_summary") or (
        "This report summarizes the current state, key findings, and recommendations "
        "to help the organization achieve its goals."
    )
    current_state = data.get("current_state") or data.get("current_state_analysis") or (
        "Overview of processes, systems, and performance based on available information."
    )
    findings = data.get("findings") or data.get("key_findings") or []
    recommendations = data.get("recommendations") or []
    next_steps = data.get("next_steps") or []

    employees_text = f"{employees}" if employees is not None else "(unspecified)"
    revenue_text = format_currency(revenue) if revenue is not None else "(unspecified)"

    md = []
    md.append(f"# Consulting Report — {name}")
    md.append("")
    md.append("## Executive Summary")
    md.append(executive_summary)
    md.append("")

    md.append("## Business Profile")
    md.append(f"- Name: {name}")
    md.append(f"- Industry: {industry}")
    md.append(f"- Employees: {employees_text}")
    md.append(f"- Annual Revenue: {revenue_text}")
    md.append("")

    md.append("## Current State Analysis")
    md.append(current_state)
    md.append("")

    md.append("## Key Findings")
    md.append(list_block([str(x) for x in findings]))
    md.append("")

    md.append("## Recommendations")
    md.append(list_block([str(x) for x in recommendations]))
    md.append("")

    md.append("## Next Steps")
    md.append(list_block([str(x) for x in next_steps]))
    md.append("")

    md.append("## Challenges to Address")
    md.append(list_block([str(x) for x in challenges]))
    md.append("")

    return "\n".join(md)
