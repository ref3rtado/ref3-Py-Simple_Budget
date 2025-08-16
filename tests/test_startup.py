import pytest
import logging
from tinydb import TinyDB, Query
import src.User_Interface as UI
import src.Simple_Budget_v02 as SB
from schema.db_schema import InitializeNewDatabase as NewDB

from datetime import date
from pathlib import Path
import json


###############################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="TestLogger", level=logging.DEBUG)
###############################################################################




def test_handle_missing_json(temp_paths):
    tmp_cfg = temp_paths["cfg"]
    tmp_json_file = Path(tmp_cfg) / "db_location.json"
    assert not tmp_json_file.exists(), "Expected False"
    startup = UI.StartupSequence(tmp_cfg)
    startup.check_location_json()
    assert tmp_json_file.exists(), "db_location.json should now be created"
   
    # We haven't specified the paths yet, need to setup a input fixture
    db_path, archive_path = startup.get_paths()
    assert db_path == None, "Expected: None"
    assert archive_path == None, "Expected: None"

def test_setting_paths_db_only(temp_paths, mock_inputs):
    responses_noname = ["y", str(temp_paths["database"]), "n"]
    path_with_name = Path(temp_paths["database"]) / "db.json"
    responses_name = ["y", str(path_with_name), "n"]
    with mock_inputs(responses_noname):
        startup_noname = UI.StartupSequence(temp_paths["cfg"])
        startup_noname.set_paths()
        db_path, archive_path = startup_noname.get_paths()
        assert db_path == path_with_name
        assert archive_path == None
    with mock_inputs(responses_name):
        startup_named = UI.StartupSequence(temp_paths["cfg"])
        db_path, archive_path = startup_named.get_paths()
        assert db_path == None, "New instance. db path should be None"
        startup_named.set_paths()
        db_path, archive_path = startup_named.get_paths()
        assert db_path == path_with_name
        
def test_setting_paths_both(temp_paths, mock_inputs):
    responses_expected_path = [
        "y", str(temp_paths["database"]), 
        "y", (temp_paths["archive"])
    ]
    bad_archive_path = Path(temp_paths["archive"]) / "db.json"
    responses_bad_path = [
        "y", temp_paths["database"],
        "y", bad_archive_path 
    ]
    with mock_inputs(responses_expected_path):
        startup_expected = UI.StartupSequence(temp_paths["cfg"])
        db_path, archive_path = startup_expected.get_paths()
        assert db_path == None, "New instance, path should be None"
        startup_expected.set_paths()
        db_path, archive_path = startup_expected.get_paths()
        assert db_path == Path(temp_paths["database"]) / "db.json"
        assert archive_path == Path(temp_paths["archive"])
    with mock_inputs(responses_bad_path):
        startup_bad_path = UI.StartupSequence(temp_paths["cfg"])
        startup_bad_path.set_paths()
        db_path, archive_path = startup_bad_path.get_paths()
        assert archive_path == Path(temp_paths["archive"]), """
        Function needs to strip file name from path.
        """

def test_no_db_at_path(temp_location_json):
    startup = UI.StartupSequence(temp_location_json)
    startup.check_location_json()
    with pytest.raises(FileNotFoundError) as db_missing:
        db_exists, archive_exists = startup.validate_paths()

def test_db_creation_default_tables(temp_location_json, mock_inputs):
    """
    Mock respones:
        "y": Yes, create a new db.json file
        "y": Yes, use default tables
    """
    responses =["y", "Y"]
    location_json = Path(temp_location_json)
    startup = UI.StartupSequence(location_json)
    startup.check_location_json()
    with mock_inputs(responses):
        startup.create_first_db()
    with open(temp_location_json, 'r') as f:
        data = json.load(f)
        db_path = Path(data.get('database_path'))
    with TinyDB(db_path) as db:
        expected_tables = {
            "Groceries",
            "Shopping",
            "Medical",
            "Pet",
            "Restaurants",
            "Drinks",
            "Entertainment",
            "Transportation",
            "Subscriptions", 
            "metadata"
        }
        actual_tables = set(db.tables())
        clogger.debug(f'Expected tables: {expected_tables}')
        clogger.debug(f'Actual tables: {actual_tables}')
        clogger.debug(
            f'Difference in sets: {expected_tables.difference(actual_tables)}'
        )
        assert expected_tables.difference(actual_tables) == set(), (
            "Expected and actual tables should be same, set difference should be empty"
        )
        metadata = db.table('metadata')
        metadata_content = metadata.get(doc_id=1)
        assert metadata_content.get("total_budget") == None
        assert metadata_content.get('creation_date') == date.today().isoformat()

@pytest.mark.skip
def test_failure(temp_paths):
    clogger.debug(temp_paths)
    assert False
