from pathlib import Path

from crm.database import Database


def test_add_and_get_customer(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    customer_id = db.add_customer("Alice", email="alice@example.com", phone="123", company="ACME")
    customer = db.get_customer(customer_id)

    assert customer is not None
    assert customer.name == "Alice"
    assert customer.email == "alice@example.com"
    assert customer.phone == "123"
    assert customer.company == "ACME"


def test_list_customers_search(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    db.add_customer("Alice Smith", email="alice@example.com")
    db.add_customer("Bob Johnson", company="Beta Corp")

    results = db.list_customers(search="Alice")
    assert len(results) == 1
    assert results[0].name == "Alice Smith"


def test_interactions_and_summary(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    customer_id = db.add_customer("Charlie")
    db.add_interaction(customer_id, "call", "Initial call")
    db.add_interaction(customer_id, "email")

    interactions = db.list_interactions(customer_id)
    assert len(interactions) == 2

    summary = db.customer_summary(customer_id)
    assert summary is not None
    assert summary["customer"].id == customer_id
    assert summary["interactions"]["call"] == 1
    assert summary["interactions"]["email"] == 1
