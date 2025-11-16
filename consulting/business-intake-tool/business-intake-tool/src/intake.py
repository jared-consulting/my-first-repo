import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List


DATA_DIR = Path("data") / "clients"


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^[0-9+()\-\s]{7,20}$")


INDUSTRIES = [
    "Retail",
    "Technology",
    "Healthcare",
    "Financial Services",
    "Manufacturing",
    "Professional Services",
    "Hospitality",
    "Education",
    "Nonprofit",
]


REVENUE_RANGES = [
    "< 100k",
    "100k - 500k",
    "500k - 1M",
    "1M - 5M",
    "5M - 10M",
    "> 10M",
]


@dataclass
class ClientIntakeRecord:
    business_name: str
    owner_name: str
    email: str
    phone: str
    industry: str
    employees: int
    years_in_business: int
    revenue_range: str
    challenges: List[str]
    goals: List[str]
    created_at: str
    slug: str


class ClientIntake:
    """Interactive CLI flow to collect and validate client business intake data."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> ClientIntakeRecord:
        print("\n=== Business Intake ===")
        business_name = self._prompt_required("Business name")
        owner_name = self._prompt_required("Owner name")
        email = self._prompt_email()
        phone = self._prompt_phone()
        industry = self._prompt_industry()
        employees = self._prompt_int("Number of employees")
        years_in_business = self._prompt_int("Years in business")
        revenue_range = self._prompt_revenue_range()

        print("\nNow let's capture the client's main challenges (3 short answers).")
        challenges = [
            self._prompt_required("Main challenge 1"),
            self._prompt_required("Main challenge 2"),
            self._prompt_required("Main challenge 3"),
        ]

        print("\nAnd finally, their top goals (3 short answers).")
        goals = [
            self._prompt_required("Goal 1"),
            self._prompt_required("Goal 2"),
            self._prompt_required("Goal 3"),
        ]

        created_at = datetime.utcnow().isoformat() + "Z"
        slug = self._slugify(business_name)

        record = ClientIntakeRecord(
            business_name=business_name,
            owner_name=owner_name,
            email=email,
            phone=phone,
            industry=industry,
            employees=employees,
            years_in_business=years_in_business,
            revenue_range=revenue_range,
            challenges=challenges,
            goals=goals,
            created_at=created_at,
            slug=slug,
        )

        self._save_record(record)
        print(
            f"\nSaved intake for '{record.business_name}' "
            f"to {self._build_path(record).relative_to(Path.cwd())}"
        )
        return record

    def _prompt_required(self, label: str) -> str:
        while True:
            value = input(f"{label}: ").strip()
            if value:
                return value
            print("  This field is required. Please enter a value.")

    def _prompt_email(self) -> str:
        while True:
            value = input("Email: ").strip()
            if not value:
                print("  Email is required.")
                continue
            if EMAIL_REGEX.match(value):
                return value
            print("  That doesn't look like a valid email address. Try again.")

    def _prompt_phone(self) -> str:
        while True:
            value = input("Phone (digits, spaces, +, -, ( )): ").strip()
            if not value:
                print("  Phone number is required.")
                continue
            if PHONE_REGEX.match(value):
                return value
            print("  Please enter a phone number using only digits, spaces, +, -, and parentheses.")

    def _prompt_int(self, label: str) -> int:
        while True:
            raw = input(f"{label}: ").strip()
            if not raw:
                print("  This field is required.")
                continue
            try:
                value = int(raw)
            except ValueError:
                print("  Please enter a whole number (no commas or symbols).")
                continue
            if value < 0:
                print("  Please enter a non-negative number.")
                continue
            return value

    def _prompt_industry(self) -> str:
        print("\nSelect industry:")
        for idx, name in enumerate(INDUSTRIES, start=1):
            print(f"  {idx}. {name}")
        while True:
            choice = input("Enter number: ").strip()
            try:
                idx = int(choice)
            except ValueError:
                print("  Please enter a number from the list.")
                continue
            if 1 <= idx <= len(INDUSTRIES):
                return INDUSTRIES[idx - 1]
            print("  Choice out of range. Try again.")

    def _prompt_revenue_range(self) -> str:
        print("\nSelect annual revenue range:")
        for idx, label in enumerate(REVENUE_RANGES, start=1):
            print(f"  {idx}. {label}")
        while True:
            choice = input("Enter number: ").strip()
            try:
                idx = int(choice)
            except ValueError:
                print("  Please enter a number from the list.")
                continue
            if 1 <= idx <= len(REVENUE_RANGES):
                return REVENUE_RANGES[idx - 1]
            print("  Choice out of range. Try again.")

    def _slugify(self, name: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", "-", name.strip().lower())
        cleaned = cleaned.strip("-")
        return cleaned or "client"

    def _build_path(self, record: ClientIntakeRecord) -> Path:
        date_str = datetime.utcnow().strftime("%Y%m%d")
        filename = f"{record.slug}-{date_str}.json"
        return self.data_dir / filename

    def _save_record(self, record: ClientIntakeRecord) -> None:
        path = self._build_path(record)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(asdict(record), f, indent=2, ensure_ascii=False)


def main() -> None:
    """Entry point for running the interactive intake directly."""
    intake = ClientIntake()
    intake.run()


if __name__ == "__main__":
    main()
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List


DATA_DIR = Path("data") / "clients"


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^[0-9+()\-\s]{7,20}$")


INDUSTRIES = [
    "Retail",
    "Technology",
    "Healthcare",
    "Financial Services",
    "Manufacturing",
    "Professional Services",
    "Hospitality",
    "Education",
    "Nonprofit",
]


REVENUE_RANGES = [
    "< 100k",
    "100k - 500k",
    "500k - 1M",
    "1M - 5M",
    "5M - 10M",
    "> 10M",
]


@dataclass
class ClientIntakeRecord:
    business_name: str
    owner_name: str
    email: str
    phone: str
    industry: str
    employees: int
    years_in_business: int
    revenue_range: str
    challenges: List[str]
    goals: List[str]
    created_at: str
    slug: str


class ClientIntake:
    """Interactive CLI flow to collect and validate client business intake data."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> ClientIntakeRecord:
        print("\n=== Business Intake ===")
        business_name = self._prompt_required("Business name")
        owner_name = self._prompt_required("Owner name")
        email = self._prompt_email()
        phone = self._prompt_phone()
        industry = self._prompt_industry()
        employees = self._prompt_int("Number of employees")
        years_in_business = self._prompt_int("Years in business")
        revenue_range = self._prompt_revenue_range()

        print("\nNow let's capture the client's main challenges (3 short answers).")
        challenges = [
            self._prompt_required("Main challenge 1"),
            self._prompt_required("Main challenge 2"),
            self._prompt_required("Main challenge 3"),
        ]

        print("\nAnd finally, their top goals (3 short answers).")
        goals = [
            self._prompt_required("Goal 1"),
            self._prompt_required("Goal 2"),
            self._prompt_required("Goal 3"),
        ]

        created_at = datetime.utcnow().isoformat() + "Z"
        slug = self._slugify(business_name)

        record = ClientIntakeRecord(
            business_name=business_name,
            owner_name=owner_name,
            email=email,
            phone=phone,
            industry=industry,
            employees=employees,
            years_in_business=years_in_business,
            revenue_range=revenue_range,
            challenges=challenges,
            goals=goals,
            created_at=created_at,
            slug=slug,
        )

        self._save_record(record)
        print(
            f"\nSaved intake for '{record.business_name}' "
            f"to {self._build_path(record).relative_to(Path.cwd())}"
        )
        return record

    def _prompt_required(self, label: str) -> str:
        while True:
            value = input(f"{label}: ").strip()
            if value:
                return value
            print("  This field is required. Please enter a value.")

    def _prompt_email(self) -> str:
        while True:
            value = input("Email: ").strip()
            if not value:
                print("  Email is required.")
                continue
            if EMAIL_REGEX.match(value):
                return value
            print("  That doesn't look like a valid email address. Try again.")

    def _prompt_phone(self) -> str:
        while True:
            value = input("Phone (digits, spaces, +, -, ( )): ").strip()
            if not value:
                print("  Phone number is required.")
                continue
            if PHONE_REGEX.match(value):
                return value
            print("  Please enter a phone number using only digits, spaces, +, -, and parentheses.")

    def _prompt_int(self, label: str) -> int:
        while True:
            raw = input(f"{label}: ").strip()
            if not raw:
                print("  This field is required.")
                continue
            try:
                value = int(raw)
            except ValueError:
                print("  Please enter a whole number (no commas or symbols).")
                continue
            if value < 0:
                print("  Please enter a non-negative number.")
                continue
            return value

    def _prompt_industry(self) -> str:
        print("\nSelect industry:")
        for idx, name in enumerate(INDUSTRIES, start=1):
            print(f"  {idx}. {name}")
        while True:
            choice = input("Enter number: ").strip()
            try:
                idx = int(choice)
            except ValueError:
                print("  Please enter a number from the list.")
                continue
            if 1 <= idx <= len(INDUSTRIES):
                return INDUSTRIES[idx - 1]
            print("  Choice out of range. Try again.")

    def _prompt_revenue_range(self) -> str:
        print("\nSelect annual revenue range:")
        for idx, label in enumerate(REVENUE_RANGES, start=1):
            print(f"  {idx}. {label}")
        while True:
            choice = input("Enter number: ").strip()
            try:
                idx = int(choice)
            except ValueError:
                print("  Please enter a number from the list.")
                continue
            if 1 <= idx <= len(REVENUE_RANGES):
                return REVENUE_RANGES[idx - 1]
            print("  Choice out of range. Try again.")

    def _slugify(self, name: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", "-", name.strip().lower())
        cleaned = cleaned.strip("-")
        return cleaned or "client"

    def _build_path(self, record: ClientIntakeRecord) -> Path:
        date_str = datetime.utcnow().strftime("%Y%m%d")
        filename = f"{record.slug}-{date_str}.json"
        return self.data_dir / filename

    def _save_record(self, record: ClientIntakeRecord) -> None:
        path = self._build_path(record)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(asdict(record), f, indent=2, ensure_ascii=False)

