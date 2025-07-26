##Script for testing interactions with the database relay module
import pytest
import unittest.mock as mock
import logging
from tinydb import TinyDB, Query
import database.db_relay as db_relay
from pathlib import Path
from schema.db_schema import db_payload as Payload
import schema.db_schema as db_schema
from datetime import date
import shutil

##############################################################################################################################
#TODO: Set up proper debug console.
from log.LogSetup import setup_logging
clogger = setup_logging(name="TestLogger", level=logging.DEBUG)
flogger = setup_logging(name="TestLogger", level=logging.DEBUG, log_file='Simple_Budget_Log.log')
##############################################################################################################################

@pytest.fixture(scope="module")
def temp_db_path(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("database") / "test_db.json"
    return db_path

@pytest.fixture(scope="function")
def test_db(temp_db_path):
    clogger.debug(f"Temporary database path: {temp_db_path}")
    db_relay.InitializeNewDatabase(db_path=temp_db_path, tables=['Groceries', 'Car', 'Shopping'], total_budget=1000.01)
    db = TinyDB(temp_db_path, sort_keys=True, indent=4, separators=(',', ': '))
    yield db
    db.close()

def test_db_initialization_tables(test_db):
    """
    Test to ensure that the temporary database is created correctly.
    Test to make sure it was created with the correct tables. 
    """
    expected_temp_tables = {'All_Tables', 'Groceries', 'Car', 'Shopping'}
    actual_temp_tables = set(test_db.tables())
    clogger.debug(expected_temp_tables.difference(actual_temp_tables)) 
    assert expected_temp_tables.difference(actual_temp_tables) == set(), "Database should contain the correct tables."

def test_db_initialization_all_table_data(test_db):
    test_date = date.today().isoformat()
    creation_date = test_db.table('All_Tables').get(doc_id=1).get('creation_date')
    total_budget = test_db.table('All_Tables').get(doc_id=1).get('total_budget')
    assert creation_date == test_date, "Database should have the correct creation date."

@pytest.fixture(scope="function")
def temp_archive_directory(temp_db_path):
    archive_path = temp_db_path.parent / "archive"
    archive_path.mkdir(exist_ok=True)
    clogger.debug(f'Temporary archive directory created at: {archive_path}')
    return archive_path


def test_rotate_database(temp_db_path, temp_archive_directory):
    clogger.debug(f"Testing database rotation with db_path: {temp_db_path} and archive_path: {temp_archive_directory}")
    clogger.debug(f'Temp DB Exists: {Path(temp_db_path).exists()} | Archive Path Exists: {temp_archive_directory.exists()}')
    db_relay.rotate_database(db_path=temp_db_path, archive_path=temp_archive_directory)
    current_date = date.today().isoformat()
    expected_archive_filename = db_schema.generate_archive_filename(current_date)
    expected_archive_file_path = temp_archive_directory.joinpath(expected_archive_filename)
    clogger.debug(f"Expected archive file path: {expected_archive_file_path}")
    assert expected_archive_file_path.exists(), "The database should be archived in the specified directory."
    
    expected_archive_filename = expected_archive_filename.replace('.json', '[1].json')
    expected_archive_file_path = expected_archive_file_path.with_name(expected_archive_filename)

    db_relay.rotate_database(db_path=temp_db_path, archive_path=temp_archive_directory)
    clogger.debug(f"Expected archive file: {expected_archive_file_path}")
    # Check if the archive file exists with the incremented name
    assert expected_archive_file_path.exists(), "The database should be archived with an incremented name in the specified directory."

def test_rotation_with_custom_initialization(temp_db_path, temp_archive_directory):
    clogger.debug('Starting test for customizing new database initialization after rotating the db')
    custom_params = {
        'creation_date': '2025-01-02',
        'total_budget': 1000.01,
    }
    clogger.debug('Instantiating new database')
    result = db_relay.rotate_database(
        db_path=temp_db_path,
        archive_path=temp_archive_directory,
        custom_params_for_new_db=custom_params,
    )
    clogger.debug("Completed db instantiation.")
    
    # Check that the root table has the values that we specified.
    db = TinyDB(temp_db_path) 
    clogger.debug("Checking contents of the root table")
    root_table = db.table('All_Tables').all()
    clogger.debug(f'root_table_contents: {root_table}')
    assert root_table[0].get('creation_date') == '2025-01-02'
    clogger.debug('Checking the total budget limit...')
    assert root_table[1].get("total_budget") == 1000.01
    
def test_add_transaction(temp_db_path):
    db = TinyDB(temp_db_path)
    payload = Payload(
        table_name="Grocery", 
        cost="25.05", 
        description="test description", 
        date="2025-02-01"
        )
    result = db_relay.add_transaction(payload, temp_db_path)
    clogger.debug(f"Return value from add_transaction [Expected is None]: {result}")
    
    # Test that the function did not raise any exceptions.
    assert result is None, "add_transaction function should return None if no exceptions are raised"

    # Test that the function successfully added the transaction    
    payload_table = payload.get_table_name()
    db_table = db.table(payload_table)
    data_added_to_db = db_table.get(doc_id=2)
    clogger.debug(f'Data found in test database: {data_added_to_db}')
    assert data_added_to_db['cost'] == "25.05", "The cost of the added transaction should be 25.05"
    assert data_added_to_db['description'] == 'test description', "The description should be \"test description\""
    assert data_added_to_db['date'] == '2025-02-01', "The date should be 2025-02-01"

def test_total_budget_updated(temp_db_path):
    total_budget, grocery_budget = db_relay.get_remaining_budget(temp_db_path, "Grocery")
    assert total_budget == 1000.01 - 25.05
    assert grocery_budget == 0.0


   

