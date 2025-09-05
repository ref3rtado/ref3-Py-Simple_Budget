import pytest
import logging
from tinydb import TinyDB, Query
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


@pytest.fixture(scope="module")
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
    
@pytest.mark.xfail(reason="Function has not been implemented yet.")
def test_add_transaction_no_UI(temp_database_file):
    payload_object = PayloadTemplate(
        category="Groceries",
        cost=10.01,
        description="Test-1",
        account="pytest",
        date="2025-01-01"
    )
    payload = payload_object.get_payload()
    DBRelay.insert_transaction(payload) #Not created yet.

    with TinyDB(temp_database_file) as db:
        table = db.table("Groceries")
        q = Query()
        results = table.search((q.description == "Test-1" & (q.cost == 10.01)))
        assert len(results) == 1, "Query should only return 1 result."
