from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Literal, Optional

ClientStatus = Literal["prospect", "active", "paused", "closed"]


@dataclass
class Contact:
    name: str
    email: str
    phone: Optional[str] = None


@dataclass
class Project:
    name: str
    description: str = ""


@dataclass
class Client:
    name: str
    contact: Contact
    projects: List[Project] = field(default_factory=list)
    status: ClientStatus = "prospect"


# Simple in-memory store keyed by client name
ClientStore = Dict[str, Client]


def create_store() -> ClientStore:
    return {}


def add_client(store: ClientStore, client: Client) -> None:
    """Add a new client to the store. Raises ValueError if it already exists."""
    key = client.name.strip()
    if not key:
        raise ValueError("Client name cannot be empty")
    if key in store:
        raise ValueError(f"Client '{key}' already exists")
    store[key] = client


def update_client_status(store: ClientStore, name: str, status: ClientStatus) -> None:
    """Update status for a client. Raises KeyError if not found."""
    key = name.strip()
    if key not in store:
        raise KeyError(f"Client '{key}' not found")
    store[key].status = status


def to_dict(store: ClientStore) -> Dict[str, dict]:
    """Serialize store to a plain dict (useful for JSON)."""
    return {k: asdict(v) for k, v in store.items()}
