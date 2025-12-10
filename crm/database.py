from __future__ import annotations

import contextlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class Customer:
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]


@dataclass
class Interaction:
    id: int
    customer_id: int
    type: str
    notes: Optional[str]
    created_at: str


class Database:
    """Lightweight SQLite wrapper for CRM data."""

    def __init__(self, db_path: Path | str = "crm.db") -> None:
        self.db_path = Path(db_path)
        self._ensure_parent_dir()
        self._initialize()

    def _ensure_parent_dir(self) -> None:
        if self.db_path.parent and not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _initialize(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    company TEXT
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(customer_id) REFERENCES customers(id)
                );
                """
            )

    @contextlib.contextmanager
    def _connection(self) -> Iterable[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def add_customer(
        self, name: str, email: Optional[str] = None, phone: Optional[str] = None, company: Optional[str] = None
    ) -> int:
        with self._connection() as conn:
            cursor = conn.execute(
                "INSERT INTO customers (name, email, phone, company) VALUES (?, ?, ?, ?)",
                (name, email, phone, company),
            )
            return int(cursor.lastrowid)

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
            if not row:
                return None
            return Customer(**row)

    def list_customers(self, search: Optional[str] = None) -> List[Customer]:
        query = "SELECT * FROM customers"
        params: tuple = ()
        if search:
            query += " WHERE name LIKE ? OR email LIKE ? OR company LIKE ?"
            pattern = f"%{search}%"
            params = (pattern, pattern, pattern)
        query += " ORDER BY name COLLATE NOCASE"
        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [Customer(**row) for row in rows]

    def add_interaction(self, customer_id: int, type: str, notes: Optional[str] = None) -> int:
        with self._connection() as conn:
            cursor = conn.execute(
                "INSERT INTO interactions (customer_id, type, notes) VALUES (?, ?, ?)",
                (customer_id, type, notes),
            )
            return int(cursor.lastrowid)

    def list_interactions(self, customer_id: int) -> List[Interaction]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM interactions WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,)
            ).fetchall()
            return [Interaction(**row) for row in rows]

    def customer_summary(self, customer_id: int) -> Optional[dict]:
        with self._connection() as conn:
            customer = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
            if not customer:
                return None
            interactions = conn.execute(
                "SELECT type, COUNT(*) as count FROM interactions WHERE customer_id = ? GROUP BY type",
                (customer_id,),
            ).fetchall()
            return {
                "customer": Customer(**customer),
                "interactions": {row["type"]: row["count"] for row in interactions},
            }
