import pytest
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
        "root": str(root_dir),
        "database": str(database_dir),
        "archive": str(archive_dir),
        "cfg": str(cfg_dir)
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