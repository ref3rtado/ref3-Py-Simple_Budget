from pathlib import Path
import json
import logging
from datetime import date
from schema.db_schema import InitializeNewDatabase as NewDBcfg
from schema.db_schema import AddTransactionPayload
from enum import Enum
import database.db_relay as DBRelay


###############################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="SimpleBudgetUI", level=logging.DEBUG)
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
                case "n":
                    print("User chose not to set the archive path.")
                case _:
                    print('Invalid input. Skipping archive directory creation.')
    
    def create_first_db(self):
        action = str(input("[REQUIRED] Create the database file? (y, n): "))
        match action.lower():
            case 'n':
                #TODO: Force quit program instead of return
                return
            case 'y':
                pass
            case _: 
                print("Invalid input. Quitting program...") #TODO, loop until valid input.
                return
        db = NewDBcfg(self.db_path)
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
                db.set_custom_tables(user_categories)
                print("Custom categories set: ")
                for category in user_categories:
                    print(category)
            case 'y':
                print("Using default categories.")
        print("Creating db.json...")
        print("You can set budget limits at the main menu.")
        DBRelay.create_db(self.db_path, db.get_db_properties())


class MainMenuOptions(Enum):
    def __new__(cls, option: str, description: str):
        obj = object.__new__(cls)
        obj._value_ = option
        obj.description = description
        return obj
    
    ADD_TRANSACTION = '1', "Add a transaction"
    VIEW_TRANSACTIONS = '2', "View recent transactions"
    VIEW_BALANCE = '3', "View total spent and remaining budget"
    VIEW_HISTORY = '4', "View historical transactions (>30 days)"
    MODIFY_BUDGET = '5', "Adjust total budget or category budgets"
    MODIFY_CATEGORIES = '6', "Add or remove categories"
    AUTOMATION_FEATURES = '7', "[PENDING]"
    ROTATE_DB = '8', "Archive the current database and create a new one"
    EXIT = '9', "Exit the application"


class MainMenu:
    def __init__(self):
        self.user_selection = None
        self.menu_options = MainMenuOptions
        pass 

    def display_main_menu(self):
        print("\n")
        print('*' * 10, "Main Menu", '*' * 10, '\n')
        for line in MainMenuOptions:
            print(f'{line.value}. {line.description}')
        print()
    
    def set_user_selection(self):
        selection = input("\nPlease select an option from the menu: ")
        try:
            clogger.debug(MainMenuOptions(selection))
            self.user_selection = MainMenuOptions(selection)
            clogger.debug(f'self.user_selection == {self.user_selection}')
        except ValueError as err:
            self.user_selection = "BAD_SELECTION"
            print(f"Invalid selection: {selection}")
        pass

class AddTransactionUI:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.payload = AddTransactionPayload()
        self.db_info = DBRelay.DatabaseInfo(db_path)
    
    def set_category(self):
        #print existing tables (enumerated)
        table_menu = {}
        for i, table in enumerate(self.db_info.tables, start=1):
            table_menu[i] = table
            print(f'{i}. {table}')
        selection = int(input(f"\nPlease select a category: "))
        self.payload.category = table_menu[selection]
        clogger.debug(f"User selected category: {self.payload.category}") 
            
        #get integer selection
        #set self.payload.category with selection
        pass

    def set_account(self):
        if self.db_info.accounts == None:
            print("No accounts have been specified yet.")
            selection = input("Enter an account name [optional]: ")
        else:
            print('Current accounts: ')
            account_menu = {}
            for i, account in enumerate(self.db_info.accounts, start=1):
                account_menu[i] = account
                print(f'{i}. {account}')
            selection = input(
                f'Select an existing account ' \
                'or type a new one [optional]: ')
        try:
            selection = int(selection)
            self.payload.account = account_menu[selection]
        except ValueError:
            selection = selection.strip().lower()
            clogger.debug('User input is NaN')
            account_added = DBRelay.add_account(self.db_path, selection)
            if account_added:
                print(f'Added account: {selection}')
            else:
                self.payload.account = selection
                print(f'Account "{selection}" not added. ' \
                      'Either it\'s an empty string or already exists')
        
    def set_transaction_info(self):
        cost_str = input("Enter the cost of the transaction [$$.cc]: ").strip()
        if cost_str[0] == "$":
            clogger.debug
            cost_str = cost_str[0:]
        try:
            cost = float(cost_str)
        except TypeError as TypeErr:
            print(f'Could not convert entered value "{cost_str}" to a float')
            dollar_val = int(input('Enter dollar amount (no cents or "$"): '))
            cent_val = int(input('Enter cents (no decimal) [optional]: '))
            cost = float(dollar_val) + float(cent_val / 100)
            clogger.debug(f"TypeError: Added dollars and cents: {cost}")
        self.payload.cost = cost
        transaction_date = input("Enter date of transaction [yyyy/mm/dd]" \
                                 "(optional): ")
        if transaction_date:
            user_date = transaction_date.split("/")
            transaction_date = date(
                int(user_date[0]), 
                int(user_date[1]), 
                int(user_date[2])
                ).isoformat()
            self.payload.date = transaction_date
        user_description = input("Enter a description (optional): ")
        if user_description:
            self.payload.description = user_description
        
    
    def insert_transaction(self):
        payload = self.payload.get_payload()
        r = DBRelay.insert_transaction(self.db_path, payload) # Response
        print(f"Transaction added to {self.payload.category} category.")
        print("-" * 10, "TOTALS", "-" * 10)
        print(f"Total spent: ${r["total_spent"]}")
        if r["total_budget"] is not None:
            remain = r["total_budget"]
            remain_statement = (
                f"Remaining budget (overall): ${remain}" if remain > 0 else (
                    f"Remaining budget (overall): ${remain} \n !Over Budget!"
                )
            )
            print(remain_statement)
        else:
            print("No overall budget currently set.")
        print(f"{"-" * 10}{self.payload.category.upper()}{"-" * 10}")
        print(f"Total spent ({self.payload.category}): {r["cat_total_spent"]}")
        if r["category_budget"] is not None:
            print(
                f"Remaining {self.payload.category.upper()} budget:" \
                f"${r['category_budget']}"
                )
        else:
            print(f"No category budget set for {self.payload.category}")

        



        


        