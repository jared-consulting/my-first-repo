import json
import sys
import traceback
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple


def is_client_record(data: Dict[str, Any]) -> bool:
    # Heuristics: client_intake.py output has name + business_name
    # Also accept records with business_name and either employees_count or industry
    if not isinstance(data, dict):
        return False
    if data.get("name") and data.get("business_name"):
        return True
    if data.get("business_name") and ("employees_count" in data or "industry" in data):
        return True
    return False


def extract_industry(data: Dict[str, Any]) -> str | None:
    ind = data.get("industry")
    if isinstance(ind, str) and ind.strip():
        return ind.strip()
    # business_analyzer data sometimes embeds under different shapes; keep simple for now
    return None


def extract_employees(data: Dict[str, Any]) -> float | None:
    if "employees_count" in data:
        try:
            return float(data["employees_count"])  # already numeric in CLI output
        except Exception:
            return None
    if "employees" in data:
        try:
            return float(data["employees"])  # from other scripts
        except Exception:
            return None
    return None


def extract_challenges(data: Dict[str, Any]) -> List[str]:
    items: List[str] = []
    mc = data.get("main_challenge")
    if isinstance(mc, str) and mc.strip():
        items.append(mc.strip())
    ch = data.get("challenges")
    if isinstance(ch, list):
        for c in ch:
            if isinstance(c, str) and c.strip():
                items.append(c.strip())
    return items


def summarize(folder: Path) -> Tuple[int, str | None, float | None, List[str]]:
    files = list(folder.glob("*.json"))
    industries: List[str] = []
    employee_counts: List[float] = []
    challenges: List[str] = []
    total_clients = 0

    for fp in files:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not is_client_record(data):
            continue
        total_clients += 1
        ind = extract_industry(data)
        if ind:
            industries.append(ind)
        emp = extract_employees(data)
        if emp is not None:
            employee_counts.append(emp)
        challenges.extend(extract_challenges(data))

    most_common_industry: str | None = None
    if industries:
        most_common_industry = Counter(industries).most_common(1)[0][0]

    avg_employees: float | None = None
    if employee_counts:
        avg_employees = sum(employee_counts) / len(employee_counts)

    # Deduplicate challenges while preserving order
    seen = set()
    dedup_challenges: List[str] = []
    for c in challenges:
        if c not in seen:
            seen.add(c)
            dedup_challenges.append(c)

    return total_clients, most_common_industry, avg_employees, dedup_challenges


def print_report(total: int, industry: str | None, avg_emp: float | None, challenges: List[str]) -> None:
    print("=== Clients Summary ===")
    print(f"Total clients: {total}")
    print(f"Most common industry: {industry or '(n/a)'}")
    if avg_emp is None:
        print("Average employee count: (n/a)")
    else:
        print(f"Average employee count: {avg_emp:.2f}")
    print("\nAll main challenges:")
    if not challenges:
        print("- (none)")
    else:
        for c in challenges:
            print(f"- {c}")


def main() -> None:
    folder = Path.cwd()
    total, industry, avg_emp, challenges = summarize(folder)
    print_report(total, industry, avg_emp, challenges)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
