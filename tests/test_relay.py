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
    db_relay.InitializeNewDatabase(db_path=temp_db_path, tables=['Groceries', 'Car', 'Shopping'], total_budget=1000.0)
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

def test_db_initialization_creation_date(test_db):
    current_date = date.today().isoformat()
    creation_date = test_db.table('All_Tables').get(doc_id=1).get('creation_date')
    assert creation_date == current_date, "Database should have the correct creation date."

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
    