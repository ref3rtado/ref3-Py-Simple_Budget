import pytest
import json
from pathlib import Path
from unittest.mock import patch

@pytest.fixture
def temp_paths(tmp_path_factory):
    root_dir = tmp_path_factory.mktemp("root")
    database_dir = root_dir / "database"
    archive_dir = root_dir / "archive"
    cfg_dir = root_dir / "cfg"

    database_dir.mkdir()
    archive_dir.mkdir()
    cfg_dir.mkdir()
    return {
        "root": root_dir,
        "database": database_dir,
        "archive": archive_dir,
        "cfg": cfg_dir
    }

def test_temp_dir_tree_exists(temp_paths):
    assert temp_paths["database"].exists()
    assert temp_paths["archive"].exists()
    assert temp_paths["cfg"].exists

@pytest.fixture
def mock_inputs():
    def _mock_inputs(responses):
        if not isinstance(responses, (list, tuple)):
            raise TypeError("mock_inputs requires either a list or tuple")
        return patch("builtins.input", side_effect=responses)
    return _mock_inputs

@pytest.fixture
def temp_location_json(temp_paths):
    db_path = Path(temp_paths["database"]) / "db.json"
    archive_path = Path(temp_paths["archive"])
    cfg_path = Path(temp_paths['cfg']) / 'db_location.json'
    payload = {
        "database_path": str(db_path),
        "archive_path": str(archive_path)        
    }
    with open(cfg_path, 'w') as f:
        json.dump(payload, f, indent=4)
    return cfg_path

def test_temp_cfg_file_created(temp_location_json, temp_paths):
    assert Path(temp_location_json).exists()
    with open(temp_location_json, "r") as f:
        data = json.load(f)
        assert data.get("database_path") == Path(temp_paths["database"])
        assert data.get("archive_path") == Path(temp_paths["archive"])