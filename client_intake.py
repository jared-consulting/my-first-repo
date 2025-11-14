import json
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Dict

EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.I)


def prompt(label: str, required: bool = True, validate=None) -> str:
    while True:
        try:
            val = input(f"{label}: ").strip()
        except EOFError:
            print("Error: input ended unexpectedly.", file=sys.stderr)
            sys.exit(1)
        if not val and required:
            print(f"{label} is required. Please enter a value.")
            continue
        if validate and val:
            msg = validate(val)
            if msg:
                print(msg)
                continue
        return val


def validate_email(v: str) -> str | None:
    if not EMAIL_RE.match(v):
        return "Please enter a valid email (e.g., name@example.com)."
    return None


def validate_int_nonneg(v: str) -> str | None:
    try:
        n = int(v.replace(",", ""))
        if n < 0:
            return "Please enter a non-negative integer."
    except ValueError:
        return "Please enter a valid integer (e.g., 25)."
    return None

def validate_phone(v: str) -> str | None:
    # Accept common phone formats but require at least 10 digits
    digits = re.sub(r"\D", "", v)
    if len(digits) < 10:
        return "Please enter a phone number with at least 10 digits."
    return None


def sanitize_filename(name: str) -> str:
    name = name.strip() or "client"
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^A-Za-z0-9_-]", "", name)
    return name or "client"


def main() -> None:
    print("\nClient Intake — CLI\n")
    name = prompt("Contact name")
    email = prompt("Email", validate=validate_email)
    phone = prompt("Phone (optional)", required=False, validate=validate_phone)
    business_name = prompt("Business name")
    employees_count = prompt("Employees count", validate=validate_int_nonneg)
    industry = prompt("Industry")
    main_challenge = prompt("Main challenge")

    data: Dict[str, Any] = {
        "name": name,
        "email": email,
        "phone": phone,
        "business_name": business_name,
        "employees_count": int(employees_count.replace(",", "")) if employees_count else 0,
        "industry": industry,
        "main_challenge": main_challenge,
    }

    base = sanitize_filename(f"{business_name}_{name}")
    out = Path(f"{base}.json")

    try:
        with out.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Failed to write JSON file '{out.resolve()}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Saved: {out.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
