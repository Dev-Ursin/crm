from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .database import Customer, Database


class CRMApp:
    def __init__(self, db_path: Path | str = "crm.db") -> None:
        self.db = Database(db_path)

    def add_customer(self, name: str, email: Optional[str], phone: Optional[str], company: Optional[str]) -> int:
        return self.db.add_customer(name=name, email=email, phone=phone, company=company)

    def list_customers(self, search: Optional[str]) -> list[Customer]:
        return self.db.list_customers(search)

    def add_interaction(self, customer_id: int, type: str, notes: Optional[str]) -> int:
        return self.db.add_interaction(customer_id, type, notes)

    def customer_detail(self, customer_id: int) -> Optional[tuple[Customer, list]]:
        customer = self.db.get_customer(customer_id)
        if not customer:
            return None
        interactions = self.db.list_interactions(customer_id)
        return customer, interactions

    def summary(self, customer_id: int) -> Optional[dict]:
        return self.db.customer_summary(customer_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple CRM command line tool")
    parser.add_argument("--db", default="crm.db", help="Path to SQLite database file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_customer = subparsers.add_parser("add-customer", help="Register a new customer")
    add_customer.add_argument("name", help="Customer name")
    add_customer.add_argument("--email", help="Email address")
    add_customer.add_argument("--phone", help="Phone number")
    add_customer.add_argument("--company", help="Company")

    list_customers = subparsers.add_parser("list-customers", help="List customers")
    list_customers.add_argument("--search", help="Filter customers by name, email or company")

    add_interaction = subparsers.add_parser("add-interaction", help="Log an interaction with a customer")
    add_interaction.add_argument("customer_id", type=int, help="Customer identifier")
    add_interaction.add_argument("--type", required=True, help="Interaction type (call, email, meeting...)")
    add_interaction.add_argument("--notes", help="Notes about the interaction")

    detail = subparsers.add_parser("show-customer", help="Show a customer and their interactions")
    detail.add_argument("customer_id", type=int, help="Customer identifier")

    summary = subparsers.add_parser("summary", help="Show aggregated info for a customer")
    summary.add_argument("customer_id", type=int, help="Customer identifier")

    return parser


def render_customer(customer: Customer) -> str:
    email = f"\nEmail: {customer.email}" if customer.email else ""
    phone = f"\nPhone: {customer.phone}" if customer.phone else ""
    company = f"\nCompany: {customer.company}" if customer.company else ""
    return f"[{customer.id}] {customer.name}{company}{email}{phone}"


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    app = CRMApp(args.db)

    if args.command == "add-customer":
        customer_id = app.add_customer(args.name, args.email, args.phone, args.company)
        print(f"Customer created with id {customer_id}")

    elif args.command == "list-customers":
        customers = app.list_customers(args.search)
        if not customers:
            print("No customers found.")
            return
        for customer in customers:
            print(render_customer(customer))

    elif args.command == "add-interaction":
        if not app.db.get_customer(args.customer_id):
            print("Customer not found.")
            return
        interaction_id = app.add_interaction(args.customer_id, args.type, args.notes)
        print(f"Interaction saved with id {interaction_id}")

    elif args.command == "show-customer":
        detail = app.customer_detail(args.customer_id)
        if not detail:
            print("Customer not found.")
            return
        customer, interactions = detail
        print(render_customer(customer))
        if interactions:
            print("\nInteractions:")
            for interaction in interactions:
                note = f" - {interaction.notes}" if interaction.notes else ""
                print(f" * [{interaction.created_at}] {interaction.type}{note}")
        else:
            print("\nNo interactions recorded.")

    elif args.command == "summary":
        summary_data = app.summary(args.customer_id)
        if not summary_data:
            print("Customer not found.")
            return
        customer = summary_data["customer"]
        stats = summary_data["interactions"]
        print(render_customer(customer))
        if not stats:
            print("\nNo interactions recorded.")
            return
        print("\nInteractions summary:")
        for type_name, count in stats.items():
            print(f" - {type_name}: {count}")


if __name__ == "__main__":
    main()
