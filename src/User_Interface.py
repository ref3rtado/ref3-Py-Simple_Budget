from pathlib import Path
import json
import logging
from schema.db_schema import InitializeNewDatabase as NewDB


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
                self.db_path = Path(data.get("database_path"))
                self.archive_path = Path(data.get("archive_path"))
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

    def validate_paths(self):
        clogger.debug("Checking if db has already been created")
        clogger.debug(f"Current path: {self.db_path}")
        valid_db = Path(self.db_path).exists()
        valid_archive = Path(self.archive_path).exists()
        if valid_db == False:
            raise FileNotFoundError(f"db.json not found at path {self.db_path} \
                                    Please create or correct the path.")
        if self.archive_path.exists() == False:
            print(f'Archive path: {self.archive_path}')
            action = str(input("Archive directory not found. Create it?"))
            match action.lower():
                case "y":
                    if self.archive_path == None:
                        self.set_paths()
                    self.archive_path.mkdir()
                    valid_archive = self.archive_path.exists()
                case "n":
                    valid_archive = False
                case _:
                    print('Invalid input. Skipping archive directory creation')
    
    def create_first_db(self):
        action = str(input("[REQUIRED] Create the database file? (y, n): "))
        match action.lower():
            case 'n':
                return
            case 'y':
                pass
            case _: 
                print("Invalid input. Quitting program...") #TODO, loop until valid input.
                return
        db = NewDB(self.db_path)
        db.set_default_tables()
        tables = db.get_tables()
        print('*' * 10, "Create first databse", '*' * 10, '\n')
        print("Current default tables: ")
        for table in tables:
            print(f'-{table}')
        action = str(input('Use default tables? (y/n): '))
        match action.lower():
            case 'n':
                user_categories = str(
                    input(
                        "Please provide comma separated " \
                        "list of custom categories."
                    ))
                user_categories = user_categories.strip().split(',')
                print("Custom categories set: ")
                for category in user_categories:
                    print(category)
            case 'y':
                print("Using default categories.")
        print("Creating db.json...")
        print("You can set budget limits at the main menu.")
        db.create_database()


            