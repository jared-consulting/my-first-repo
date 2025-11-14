import json
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List

EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.I)
from colorama import init as colorama_init, Fore, Style

colorama_init(autoreset=True)


def input_line(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        print(Fore.RED + "Input ended unexpectedly." + Style.RESET_ALL, file=sys.stderr)
        sys.exit(1)


def prompt(label: str, required: bool = True, validate=None) -> str:
    while True:
        val = input_line(f"{label}: ").strip()
        if not val and required:
            print(Fore.RED + f"{label} is required. Please enter a value." + Style.RESET_ALL)
            continue
        if validate and val:
            msg = validate(val)
            if msg:
                print(Fore.RED + msg + Style.RESET_ALL)
                continue
        return val


def validate_email(v: str) -> str | None:
    if not EMAIL_RE.match(v.strip()):
        return "Please enter a valid email (e.g., name@example.com)."
    return None


def validate_phone(v: str) -> str | None:
    digits = re.sub(r"\D", "", v)
    if len(digits) < 10:
        return "Please enter a phone number with at least 10 digits."
    return None


def validate_employees(v: str) -> str | None:
    try:
        n = int(v.replace(",", ""))
        if n < 0:
            return "Please enter a non-negative integer."
    except ValueError:
        return "Please enter a valid integer (e.g., 25)."
    return None


def sanitize_filename(name: str) -> str:
    name = name.strip() or "client"
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^A-Za-z0-9_-]", "", name)
    return name or "client"


def save_client(record: Dict[str, Any]) -> Path:
    base = sanitize_filename(f"{record.get('business_name','')}_{record.get('name','')}") or "client"
    out = Path(f"{base}.json")
    with out.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return out


def is_client_record(data: Dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
    if data.get("name") and data.get("business_name"):
        return True
    if data.get("business_name") and ("employees_count" in data or "industry" in data):
        return True
    return False


def extract_field(data: Dict[str, Any], *keys: str) -> Any:
    for k in keys:
        if k in data and data[k] not in (None, ""):
            return data[k]
    return None


def view_all_clients(folder: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for fp in folder.glob("*.json"):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not is_client_record(data):
            continue
        # Normalize to a display-friendly dict
        items.append({
            "file": fp.name,
            "name": extract_field(data, "name", "contact_name") or "(unknown)",
            "email": extract_field(data, "email", "contact_email") or "",
            "business_name": extract_field(data, "business_name") or "(unknown)",
            "industry": extract_field(data, "industry") or "",
            "employees": extract_field(data, "employees_count", "employees") or "",
            "main_challenge": extract_field(data, "main_challenge") or "",
        })
    return items


def print_table(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        print(Fore.YELLOW + "No client files found." + Style.RESET_ALL)
        return
    headers = ["file", "name", "email", "business_name", "industry", "employees", "main_challenge"]
    colw = {h: max(len(h), *(len(str(r.get(h, ""))) for r in rows)) for h in headers}
    line = " | ".join((Fore.CYAN + h + Style.RESET_ALL).ljust(colw[h] + len(Fore.CYAN + Style.RESET_ALL)) for h in headers)
    sep = "-+-".join("-" * colw[h] for h in headers)
    print(line)
    print(sep)
    for r in rows:
        print(" | ".join(str(r.get(h, "")).ljust(colw[h]) for h in headers))


def generate_summary(folder: Path) -> None:
    try:
        import clients_summary as cs  # reuse summary functions if present
        total, industry, avg_emp, challenges = cs.summarize(folder)
        cs.print_report(total, industry, avg_emp, challenges)
    except Exception:
        # Fallback minimal summary
        rows = view_all_clients(folder)
        total = len(rows)
        industry_counts: Dict[str, int] = {}
        emp_values: List[float] = []
        challenges: List[str] = []
        for r in rows:
            ind = str(r.get("industry") or "").strip()
            if ind:
                industry_counts[ind] = industry_counts.get(ind, 0) + 1
            try:
                if r.get("employees") not in (None, ""):
                    emp_values.append(float(r["employees"]))
            except Exception:
                pass
            mc = str(r.get("main_challenge") or "").strip()
            if mc:
                challenges.append(mc)
        most_common_industry = None
        if industry_counts:
            most_common_industry = max(industry_counts.items(), key=lambda kv: kv[1])[0]
        avg_emp = sum(emp_values) / len(emp_values) if emp_values else None
        print(Fore.CYAN + "=== Clients Summary ===" + Style.RESET_ALL)
        print(Fore.GREEN + f"Total clients: {total}" + Style.RESET_ALL)
        print(f"Most common industry: {most_common_industry or '(n/a)'}")
        print(f"Average employee count: {avg_emp:.2f}" if avg_emp is not None else "Average employee count: (n/a)")
        print(Fore.CYAN + "\nAll main challenges:" + Style.RESET_ALL)
        if challenges:
            for c in dict.fromkeys(challenges):  # preserve order, dedupe
                print(f"- {c}")
        else:
            print("- (none)")


def export_summary_markdown(folder: Path, out: Path | None = None) -> None:
    try:
        import clients_summary as cs
        total, industry, avg_emp, challenges = cs.summarize(folder)
    except Exception:
        rows = view_all_clients(folder)
        total = len(rows)
        industry_counts: Dict[str, int] = {}
        emp_values: List[float] = []
        challenges = []
        for r in rows:
            ind = str(r.get("industry") or "").strip()
            if ind:
                industry_counts[ind] = industry_counts.get(ind, 0) + 1
            try:
                if r.get("employees") not in (None, ""):
                    emp_values.append(float(r["employees"]))
            except Exception:
                pass
            mc = str(r.get("main_challenge") or "").strip()
            if mc:
                challenges.append(mc)
        industry = max(industry_counts.items(), key=lambda kv: kv[1])[0] if industry_counts else None
        avg_emp = (sum(emp_values) / len(emp_values)) if emp_values else None

    # Build markdown
    lines: List[str] = []
    lines.append("# Clients Summary")
    lines.append("")
    lines.append(f"- Total clients: {total}")
    lines.append(f"- Most common industry: {industry or '(n/a)'}")
    lines.append(f"- Average employee count: {f'{avg_emp:.2f}' if avg_emp is not None else '(n/a)'}")
    lines.append("")
    lines.append("## Main Challenges")
    if challenges:
        # dedupe preserve order
        seen = set()
        for c in challenges:
            if c not in seen:
                seen.add(c)
                lines.append(f"- {c}")
    else:
        lines.append("- (none)")

    content = "\n".join(lines) + "\n"
    target = out or folder / "clients_summary.md"
    try:
        target.write_text(content, encoding="utf-8")
        print(f"Markdown summary written to: {target.resolve()}")
    except OSError as e:
        print(f"Failed to write markdown file: {e}", file=sys.stderr)


def add_new_client() -> None:
    print("\nAdd New Client")
    name = prompt("Contact name")
    email = prompt("Email", validate=validate_email)
    phone = prompt("Phone (optional)", required=False, validate=validate_phone)
    business_name = prompt("Business name")
    employees_count = prompt("Employees count", validate=validate_employees)
    industry = prompt("Industry")
    main_challenge = prompt("Main challenge")
    record = {
        "name": name,
        "email": email,
        "phone": phone,
        "business_name": business_name,
        "employees_count": int(employees_count.replace(",", "")) if employees_count else 0,
        "industry": industry,
        "main_challenge": main_challenge,
    }
    try:
        out = save_client(record)
        print(Fore.GREEN + f"Saved: {out.resolve()}" + Style.RESET_ALL)
    except OSError as e:
        print(Fore.RED + f"Failed to save client file: {e}" + Style.RESET_ALL, file=sys.stderr)


def main() -> None:
    while True:
        print("\n" + Fore.CYAN + "Client Menu" + Style.RESET_ALL)
        print(Fore.WHITE + "1)" + Style.RESET_ALL + " Add new client")
        print(Fore.WHITE + "2)" + Style.RESET_ALL + " View all clients")
        print(Fore.WHITE + "3)" + Style.RESET_ALL + " Generate summary report")
        print(Fore.WHITE + "4)" + Style.RESET_ALL + " Export summary report (Markdown)")
        print(Fore.WHITE + "5)" + Style.RESET_ALL + " Exit")
        choice = input_line(Fore.YELLOW + "Select an option (1-5): " + Style.RESET_ALL).strip()
        if choice == "1":
            add_new_client()
        elif choice == "2":
            rows = view_all_clients(Path.cwd())
            print()
            print_table(rows)
        elif choice == "3":
            print()
            generate_summary(Path.cwd())
        elif choice == "4":
            print()
            export_summary_markdown(Path.cwd())
        elif choice == "5":
            print("Goodbye.")
            return
        else:
            print("Please enter a number 1-4.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
