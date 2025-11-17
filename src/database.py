import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional


# By default, align with client_intake.py which writes JSON files
# to the project root (base_dir). We keep CLIENTS_SUBDIR for
# potential future customization but default to the root.
CLIENTS_SUBDIR = ""


@dataclass
class ClientRecord:
    """Lightweight wrapper for a client JSON file on disk."""

    filename: str
    path: str
    data: Dict[str, Any]

    @property
    def business_name(self) -> Optional[str]:
        # Support both the richer intake schema and the simpler
        # client_intake.py schema which uses either "business_name"
        # or just "name".
        return self.data.get("business_name") or self.data.get("name")

    @property
    def industry(self) -> Optional[str]:
        return self.data.get("industry")

    @property
    def date(self) -> Optional[datetime]:
        """Best-effort parse of date from filename pattern {name}-YYYY-MM-DD.json."""
        base = os.path.basename(self.filename)
        name, ext = os.path.splitext(base)
        if ext.lower() != ".json":
            return None

        # Try to parse final 10 chars as YYYY-MM-DD
        if len(name) >= 11:
            candidate = name[-10:]
            try:
                return datetime.strptime(candidate, "%Y-%m-%d")
            except ValueError:
                return None
        return None


class ClientDatabase:
    """Convenience API for working with client JSON files on disk.

    Works with JSON files stored in `data/clients/` relative to the project root.
    """

    def __init__(self, base_dir: Optional[str] = None) -> None:
        # Default to project root (one level up from src/)
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = base_dir
        self.clients_dir = os.path.join(self.base_dir, CLIENTS_SUBDIR) or self.base_dir

    # ------------------------------------------------------------------
    # Core helpers
    # ------------------------------------------------------------------
    def _iter_client_files(self) -> Iterable[str]:
        if not os.path.isdir(self.clients_dir):
            return []
        for name in os.listdir(self.clients_dir):
            if name.lower().endswith(".json"):
                yield os.path.join(self.clients_dir, name)

    def _load_json(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Client file not found: {path}") from None
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Invalid JSON in client file: {path}\n{exc}") from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def list_clients(self) -> List[ClientRecord]:
        """Return all clients as `ClientRecord` objects.

        If the directory does not exist, returns an empty list.
        """
        records: List[ClientRecord] = []
        if not os.path.isdir(self.clients_dir):
            return records

        for path in self._iter_client_files():
            filename = os.path.basename(path)
            try:
                data = self._load_json(path)
            except (FileNotFoundError, ValueError):
                # Skip unreadable or invalid files but continue.
                continue
            records.append(ClientRecord(filename=filename, path=path, data=data))
        return sorted(records, key=lambda r: (r.date or datetime.min, r.filename))

    def load_client(self, filename: str) -> ClientRecord:
        """Load a specific client by JSON filename (e.g., 'acme-2025-11-16.json')."""
        path = os.path.join(self.clients_dir, filename)
        data = self._load_json(path)
        return ClientRecord(filename=filename, path=path, data=data)

    def search_clients(
        self,
        *,
        business_name: Optional[str] = None,
        industry: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> List[ClientRecord]:
        """Search clients by business name, industry, or exact date.

        - Matching is case-insensitive for strings.
        - `date` compares against the parsed date from the filename.
        """
        all_clients = self.list_clients()
        if not any([business_name, industry, date]):
            return all_clients

        def matches(record: ClientRecord) -> bool:
            if business_name:
                bn = (record.business_name or "").lower()
                if business_name.lower() not in bn:
                    return False
            if industry:
                ind = (record.industry or "").lower()
                if industry.lower() not in ind:
                    return False
            if date:
                if not record.date or record.date.date() != date.date():
                    return False
            return True

        return [rec for rec in all_clients if matches(rec)]

    def update_client(self, filename: str, updates: Dict[str, Any]) -> ClientRecord:
        """Update an existing client JSON file with the given fields.

        - Loads the current JSON.
        - Applies `updates` as a shallow update.
        - Writes the file back to disk.
        - Returns the updated `ClientRecord`.
        """
        record = self.load_client(filename)
        record.data.update(updates)

        os.makedirs(self.clients_dir, exist_ok=True)
        with open(record.path, "w", encoding="utf-8") as f:
            json.dump(record.data, f, indent=2, ensure_ascii=False)

        return record

    def export_to_csv(self, csv_path: Optional[str] = None) -> str:
        """Export all client JSON records to a CSV file.

        - If `csv_path` is None, creates `clients_export.csv` in the base dir.
        - Uses a flexible header built from the union of all keys.
        - Returns the path to the CSV file.
        """
        clients = self.list_clients()
        if not clients:
            # Create an empty file with just headers if desired
            if csv_path is None:
                csv_path = os.path.join(self.base_dir, "clients_export.csv")
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["filename"])
            return csv_path

        # Determine CSV headers: filename + all JSON keys across records
        all_keys: set[str] = set()
        for rec in clients:
            all_keys.update(rec.data.keys())
        fieldnames = ["filename"] + sorted(all_keys)

        if csv_path is None:
            csv_path = os.path.join(self.base_dir, "clients_export.csv")

        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for rec in clients:
                row = {key: rec.data.get(key, "") for key in all_keys}
                row["filename"] = rec.filename
                writer.writerow(row)

        return csv_path


__all__ = ["ClientDatabase", "ClientRecord"]
