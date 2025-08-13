from pathlib import Path
import json
import logging


###############################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="SimpleBudget", level=logging.DEBUG)
###############################################################################


class StartupSequence:
    """
    Contains the methods to get or set the necessary files.
    params: test_cfg [optional] str: Pass a temp cfg file for tests
    """
    def __init__(self, test_cfg=None):
        self.db_path = None
        self.archive_path = None
        self.cfg_path = test_cfg
    
    def check_location_json(self) -> None:
        if self.cfg_path: # Primarily for testing         
            if self.cfg_path.is_dir():
                self.cfg_path = self.cfg_path / "db_location.json"
            clogger.debug(f'self.cfg_path set to {self.cfg_path}')
            clogger.debug(f'Does it exist?: {self.cfg_path.exists()}')
        else:
            self.cfg_path = (
                Path(__file__).parent.parent / "cfg" / "db_location.json"
                )
            print(self.cfg_path)
        if self.cfg_path.exists():
            clogger.debug("db_location.json found. Getting paths...")
            with open(self.cfg_path, "r") as f:
                data = json.load(f)
                clogger.debug(f"json data: {data}")
                self.db_path = data.get("database_path")
                self.archive_path = data.get("archive_path")
                print(self.db_path)
                print(self.archive_path)            
        else:
            print("json file does not exist.")
            payload = {
                "database_path": None,
                "archive_path": None
            }
            with open(self.cfg_path, "w") as f:
                json.dump(payload, f, indent=4)
    
    def get_paths(self) -> tuple:
        return self.db_path, self.archive_path
    
    def set_paths(self) -> None:
        if self.db_path == None:
            action = str(input(
                """No database path listed. [REQUIRED]
                Would you like to add it? (y, n): """
            ))
            match action.lower():
                case "y":
                    user_db_path = str(input("Enter path: "))
                    print(f"Entered path: {user_db_path}")
                    user_db_path = Path(user_db_path)
                    if user_db_path.is_dir():
                        self.db_path = Path(user_db_path) / "db.json"
                    else:
                        self.db_path = Path(user_db_path)
                case "n":
                    self.db_path = None
                    print("User chose not to enter path.")
                    print(
                        "You can manually set it within", end=''
                        "./cfg/db_location.json"
                        )
                    print("Closing program...")
                case _:
                    self.db_path = None                    
                    print("Invalid input.")
                    print(
                        "You can manually set it within", end=''
                        "./cfg/db_location.json"
                        )
                    print("Closing program...")
        if self.archive_path == None:
            action = str(input(
                """No archive path listed. [OPTIONAL]
                Would you like to add it? (y, n): """
            ))
            match action.lower():
                case "y":
                    user_archive_path = str(input("Enter path: "))
                    print(f'Entered path: {user_archive_path}')
                    user_path = Path(user_archive_path)
                    if user_path.is_dir():
                        self.archive_path = user_path
                    else:
                        stripped_path = user_path.parent
                        self.archive_path = stripped_path
                        print(f"Archive path needs to be a directory/folder.")
                        print(f"Modified and set path to: {self.archive_path}")

                case "n":
                    self.archive_path = None
                    print("User chose not to enter path.")
                    print(
                        "You can manually set it within", end=''
                        "./cfg/db_location.json"
                        )
                case _:
                    self.archive_path = None                    
                    print("Invalid input.")
                    print(
                        "You can manually set it within", end=''
                        "./cfg/db_location.json"
                        )

    def validate_path(self) -> bool:
        clogger.debug("Checking if db has already been created")
        clogger.debug(f"Current path: {self.db_path}")                    
        return Path(self.db_path).exists()


            