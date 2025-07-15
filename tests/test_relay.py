##Script for testing interactions with the database relay module
import pytest
import unittest.mock as mock
import logging
from tinydb import TinyDB, Query
import database.db_relay as db_relay
from pathlib import Path

##############################################################################################################################
#TODO: Set up proper debug console.
from log.LogSetup import setup_logging
clogger = setup_logging(name="TestLogger", level=logging.DEBUG)
flogger = setup_logging(name="TestLogger", level=logging.DEBUG, log_file='Simple_Budget_Log.log')
##############################################################################################################################

@pytest.fixture
def setup_db():
    temporary_tables = ['Groceries', 'Car', 'Shopping']
    path_to_temp_db = Path(__name__).parent.joinpath('test_db.json')
    db_relay.InitializeNewDatabase(db_path=path_to_temp_db, tables=temporary_tables, total_budget=1000.0)
    db = TinyDB(path_to_temp_db, sort_keys=True, indent=4, separators=(',', ': '))
    yield db
    db.close()  # Ensure the database is closed after the test
    try:
        Path(path_to_temp_db).unlink()  # Clean up the temporary database file after the test
    except FileNotFoundError:
        clogger.warning("Temporary database file not found for cleanup.")

def test_db_initialization(setup_db):
    """
    Test to ensure that the temporary database is created correctly.
    Test to make sure it was created with the correct tables. 
    """
    temp_db_path = Path(__name__).parent.joinpath('test_db.json')
    assert Path(temp_db_path).exists(), "Temporary database file should exist."   

    expected_temp_tables = {'_default', 'Groceries', 'Car', 'Shopping'}
    actual_temp_tables = set(setup_db.tables())
    clogger.debug(expected_temp_tables.difference(actual_temp_tables)) 
    # There should be no difference between expected and actual tables, hence true if set is empty.   
    assert expected_temp_tables.difference(actual_temp_tables) == set(), "Database should contain the correct tables."
    

    