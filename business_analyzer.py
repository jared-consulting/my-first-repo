import json
import sys
import traceback
import time
from pathlib import Path
from typing import List, Dict, Any

from consulting.data_processing import sanitize_filename
from consulting.analysis import build_summary
from consulting.reporting import build_report_text


essential_prompt: str = (
    "Enter {label}{hint}: "
)


def prompt_nonempty(label: str, hint: str = "") -> str:
    while True:
        try:
            value = input(essential_prompt.format(label=label, hint=f" ({hint})" if hint else "")).strip()
        except EOFError:
            print("Error: input ended unexpectedly while reading required field.", file=sys.stderr)
            sys.exit(1)
        if value:
            return value
        print(f"{label} is required. Please enter a value.")


def prompt_int(label: str, hint: str = "") -> int:
    while True:
        raw = prompt_nonempty(label, hint)
        try:
            val = int(raw.replace(",", ""))
            if val < 0:
                raise ValueError("must be non-negative")
            return val
        except ValueError:
            print(f"Invalid {label.lower()}. Please enter a valid non-negative integer (e.g., 25). You entered: '{raw}'")


def prompt_float(label: str, hint: str = "") -> float:
    while True:
        raw = prompt_nonempty(label, hint)
        try:
            # Allow commas and $ in input
            cleaned = raw.replace(",", "").replace("$", "")
            val = float(cleaned)
            if val < 0:
                raise ValueError("must be non-negative")
            return val
        except ValueError:
            print(f"Invalid {label.lower()}. Please enter a valid non-negative number (e.g., 1250000 or 1,250,000). You entered: '{raw}'")


def prompt_challenges(max_items: int = 3) -> List[str]:
    print(f"Enter up to {max_items} main challenges. Press Enter to skip remaining.")
    items: List[str] = []
    for i in range(1, max_items + 1):
        try:
            val = input(f"  Challenge {i}: ").strip()
        except EOFError:
            print("Warning: input ended unexpectedly; proceeding with collected challenges.", file=sys.stderr)
            break
        if not val:
            break
        items.append(val)
    return items


def confirm(prompt: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        try:
            ans = input(f"{prompt} {suffix} ").strip().lower()
        except EOFError:
            return default
        if not ans:
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer 'y' or 'n'.")


def progress(task: str, steps: int = 20, delay: float = 0.03) -> None:
    print(f"{task} ", end="", flush=True)
    for _ in range(steps):
        print("█", end="", flush=True)
        time.sleep(delay)
    print(" done.")


def main() -> None:
    print("\nJared Consulting — Business Analyzer\n")

    business_name = prompt_nonempty("Business name")
    industry = prompt_nonempty("Industry")
    employees = prompt_int("Number of employees", hint="integer, e.g., 25")
    revenue = prompt_float("Annual revenue", hint="e.g., 1250000 or $1,250,000")
    challenges = prompt_challenges(max_items=3)

    data = {
        "business_name": business_name,
        "industry": industry,
        "employees": employees,
        "annual_revenue": revenue,
        "challenges": challenges,
    }

    # Save JSON named after the business
    base = sanitize_filename(business_name)
    json_path = Path(f"{base}.json")
    report_path = Path(f"{base}_report.txt")

    # Show summary and confirm before writing
    summary = build_summary(data)
    print(summary)
    if not confirm("Save this information and generate report?", default=True):
        print("Canceled. No files were written.")
        return

    try:
        progress(f"Saving {json_path.name}")
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Failed to write JSON file '{json_path.resolve()}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Saved data to: {json_path.resolve()}")

    # Write text report
    report_text = build_report_text(data)
    try:
        progress(f"Creating {report_path.name}")
        with report_path.open("w", encoding="utf-8") as f:
            f.write(report_text)
    except OSError as e:
        print(f"Failed to write report file '{report_path.resolve()}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Report created: {report_path.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
