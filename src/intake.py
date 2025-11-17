import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^[0-9\-\+\(\)\s]{7,20}$")


@dataclass
class ClientData:
    business_name: str
    owner_name: str
    email: str
    phone: str
    industry: str
    num_employees: int
    years_in_business: float
    annual_revenue_range: str
    main_challenges: List[str]
    goals: List[str]


class ClientIntake:
    """Handles interactive client intake via the command line."""

    INDUSTRIES = [
        "Technology",
        "Retail",
        "Healthcare",
        "Finance",
        "Manufacturing",
        "Hospitality",
        "Professional Services",
        "Other",
    ]

    ANNUAL_REVENUE_RANGES = [
        "<$100k",
        "$100k - $500k",
        "$500k - $1M",
        "$1M - $5M",
        "$5M - $10M",
        ">$10M",
    ]

    def run(self) -> None:
        """Run the interactive intake process."""
        print("=== Client Intake Form ===")
        print("Please answer the following questions. Press Ctrl+C at any time to exit.\n")

        try:
            client_data = self.collect_data()
        except KeyboardInterrupt:
            print("\nIntake cancelled by user.")
            return

        try:
            path = self.save(client_data)
        except Exception as exc:  # noqa: BLE001
            print("\nAn unexpected error occurred while saving the data:")
            print(str(exc))
            return

        print("\nThank you. Your information has been saved.")
        print(f"File: {path}")

    def collect_data(self) -> ClientData:
        business_name = self._prompt_required("Business name")
        owner_name = self._prompt_required("Owner name")
        email = self._prompt_email()
        phone = self._prompt_phone()
        industry = self._prompt_industry()
        num_employees = self._prompt_int("Number of employees", minimum=0)
        years_in_business = self._prompt_float("Years in business", minimum=0.0)
        annual_revenue_range = self._prompt_choice(
            "Annual revenue range",
            self.ANNUAL_REVENUE_RANGES,
        )

        print("\nNow a few questions about your current challenges.")
        main_challenges = [
            self._prompt_required("Main challenge #1"),
            self._prompt_required("Main challenge #2"),
            self._prompt_required("Main challenge #3"),
        ]

        print("\nAnd finally, your goals.")
        goals = [
            self._prompt_required("Goal #1"),
            self._prompt_required("Goal #2"),
            self._prompt_required("Goal #3"),
        ]

        return ClientData(
            business_name=business_name,
            owner_name=owner_name,
            email=email,
            phone=phone,
            industry=industry,
            num_employees=num_employees,
            years_in_business=years_in_business,
            annual_revenue_range=annual_revenue_range,
            main_challenges=main_challenges,
            goals=goals,
        )

    def save(self, client_data: ClientData) -> str:
        """Save client data to a JSON file and return the file path."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_business_name = self._slugify(client_data.business_name)
        filename = f"{safe_business_name}-{date_str}.json"

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        clients_dir = os.path.join(base_dir, "data", "clients")
        os.makedirs(clients_dir, exist_ok=True)

        path = os.path.join(clients_dir, filename)
        data: Dict[str, Any] = asdict(client_data)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return path

    def _prompt_required(self, label: str) -> str:
        while True:
            value = input(f"{label}: ").strip()
            if value:
                return value
            print("This field is required. Please enter a value.")

    def _prompt_email(self) -> str:
        while True:
            email = input("Email: ").strip()
            if not email:
                print("Email is required. Please enter a value.")
                continue
            if EMAIL_REGEX.match(email):
                return email
            print("That doesn't look like a valid email address. Please try again.")

    def _prompt_phone(self) -> str:
        while True:
            phone = input("Phone (include area code): ").strip()
            if not phone:
                print("Phone number is required. Please enter a value.")
                continue
            if PHONE_REGEX.match(phone):
                return phone
            print(
                "That doesn't look like a valid phone number. Please use digits and common",
            )
            print("punctuation only (e.g., 555-123-4567)." )

    def _prompt_industry(self) -> str:
        print("\nSelect your industry:")
        for idx, name in enumerate(self.INDUSTRIES, start=1):
            print(f"  {idx}. {name}")

        while True:
            choice = input("Enter the number for your industry: ").strip()
            if not choice.isdigit():
                print("Please enter a number from the list above.")
                continue
            index = int(choice)
            if 1 <= index <= len(self.INDUSTRIES):
                return self.INDUSTRIES[index - 1]
            print("That isn't a valid option. Please try again.")

    def _prompt_choice(self, label: str, options: List[str]) -> str:
        print(f"\n{label}:")
        for idx, option in enumerate(options, start=1):
            print(f"  {idx}. {option}")

        while True:
            choice = input("Enter the number for the best match: ").strip()
            if not choice.isdigit():
                print("Please enter a number from the list above.")
                continue
            index = int(choice)
            if 1 <= index <= len(options):
                return options[index - 1]
            print("That isn't a valid option. Please try again.")

    def _prompt_int(self, label: str, minimum: int | None = None) -> int:
        while True:
            raw = input(f"{label}: ").strip()
            if not raw:
                print("This field is required. Please enter a number.")
                continue
            try:
                value = int(raw)
            except ValueError:
                print("Please enter a whole number (no decimals).")
                continue
            if minimum is not None and value < minimum:
                print(f"Please enter a value greater than or equal to {minimum}.")
                continue
            return value

    def _prompt_float(self, label: str, minimum: float | None = None) -> float:
        while True:
            raw = input(f"{label}: ").strip()
            if not raw:
                print("This field is required. Please enter a number.")
                continue
            try:
                value = float(raw)
            except ValueError:
                print("Please enter a number (you can use decimals, e.g., 2.5).")
                continue
            if minimum is not None and value < minimum:
                print(f"Please enter a value greater than or equal to {minimum}.")
                continue
            return value

    def _slugify(self, value: str) -> str:
        """Create a filesystem-safe slug from the business name."""
        value = value.strip().lower()
        # Replace spaces and consecutive whitespace with a single dash
        value = re.sub(r"\s+", "-", value)
        # Remove any character that is not alphanumeric, dash, or underscore
        value = re.sub(r"[^a-z0-9\-_]", "", value)
        return value or "client"


if __name__ == "__main__":
    intake = ClientIntake()
    intake.run()
