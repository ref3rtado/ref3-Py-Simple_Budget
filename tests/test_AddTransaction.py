import pytest
import logging
from tinydb import TinyDB, Query
from tinydb import operations as DBOp
import src.User_Interface as UI
import src.Simple_Budget_v02 as SBMain
import database.db_relay as DBRelay
from schema.db_schema import InitializeNewDatabase as DBTemplate
from schema.db_schema import AddTransactionPayload as PayloadTemplate

from datetime import date
from pathlib import Path
import json


###############################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="TestAddTransaction", level=logging.DEBUG)
###############################################################################


@pytest.fixture
def temp_database_file(temp_paths):
    db_file = Path(temp_paths["database"]) / "test_db.json"
    clogger.debug(f'temp_database: using file {db_file}')
    new_db = DBTemplate(db_file)
    new_db.set_default_tables()
    new_db.set_total_budget(1000.00)
    db_props = new_db.get_db_properties()
    DBRelay.create_db(db_file, db_props)
    
    yield db_file

    try:
        db_file.unlink(missing_ok=True)
    except Exception:
        pass
    
def test_add_transaction_no_UI(temp_database_file):
    # Grocery payload will test with a category budget
    # Drinks payload will test with no category budget
    grocery_transaction = PayloadTemplate(
        category="Groceries",
        cost=10.01,
        description="Test with cat budget",
        account="pytest",
        date="2025-01-01"
    )
    drinks_transaction = PayloadTemplate(
        category="Drinks",
        cost=40,
        description="Test without cat budget",
        account="pytest",
        date="2025-01-01"
    )
    grocery_payload = grocery_transaction.get_payload()
    drinks_payload = drinks_transaction.get_payload()
    with TinyDB(temp_database_file) as db:
        clogger.debug(f"Adding budget to Groceries table")
        grocery_table = db.table("Groceries")
        grocery_table.update(DBOp.set("category_budget", 100), doc_ids=[1])
        clogger.debug(grocery_table) 
    DBRelay.insert_transaction(temp_database_file, grocery_payload)
    DBRelay.insert_transaction(temp_database_file, drinks_payload)

    # Assert both transactions added
    with TinyDB(temp_database_file) as db:
        q = Query()
        results = db.table("Groceries").search(q.account == "pytest")
        results.append(db.table("Drinks").search(q.account == "pytest"))         
        assert len(results) == 2, "Query should return 2 results."
    # Check that metadata was updated
        metadata = db.table("metadata").get(doc_id=1)
        test_transaction_cost = grocery_transaction.cost + drinks_transaction.cost
        assert metadata.get("total_spent") == test_transaction_cost
        assert metadata.get("total_budget") == (1000 - test_transaction_cost)
    # Check category budget & total spent values
        cat_with_budget = db.table("Groceries").get(doc_id=1)
        clogger.debug(cat_with_budget)
        assert cat_with_budget["category_budget"] == 100 - grocery_transaction.cost, (
            f"Grocery budget should be 100 - {grocery_transaction.cost}"
        )
        assert cat_with_budget["total_spent"] == grocery_transaction.cost, (
            f"Total spent for groceries should be {grocery_transaction.cost}"
        )
        cat_no_budget = db.table("Drinks").get(doc_id=1)
        assert cat_no_budget["category_budget"] == None, (
            f"Drinks total budget should not be modified"
        )
        assert cat_no_budget["total_spent"] == drinks_transaction.cost, (
            f"Total spent for drinks should be {drinks_transaction.cost}"
        )