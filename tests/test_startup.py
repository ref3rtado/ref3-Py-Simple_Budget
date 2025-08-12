import pytest
import logging
from tinydb import TinyDB, Query
import src.User_Interface as UI
import src.Simple_Budget_v02 as SB

from datetime import date
from pathlib import Path


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
    responses_noname = ["y", temp_paths["database"], "n"]
    path_with_name = Path(temp_paths["database"]) / "db.json"
    responses_name = ["y", path_with_name, "n"]
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
        "y", temp_paths["database"], 
        "y", temp_paths["archive"]
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
@pytest.mark.skip
def test_failure(temp_paths):
    clogger.debug(temp_paths)
    assert False
