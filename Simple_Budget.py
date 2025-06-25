## Main Script for Simple Budget Application ##
#TODO: Import db_relay module

#TODO: On startup, check if the database exists by talking to db_relay.py

#TODO: Print a welcome message, interaction menu, and prompt for user input
##Example: 1) Add Transaction | 2) Check Balance | 3) Modify Tables | 4) Exit
##On "1"
### Pull and enumerate the columns in the database, present as numbered options -- 1) Grocery, 2) Shopping, etc. 
#### On "1"
##### Prompt for amount, optional description, and date
###### On enter, print something like "Transaction added" /n "Current Balance: $X.XX"

##############################################################################################################################

import database.db_relay as db
import logging
import sys
from pathlib import Path
from enum import Enum
from schema.ui_prompts import MainMenuOptions as MainMenu
from schema.ui_prompts import add_transaction_ui_flow as AddTransaction

##############################################################################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="SimpleBudgetLogger", level=logging.INFO)
flogger = setup_logging(name="SimpleBudget", level=logging.DEBUG, log_file='Simple_Budget_Log.log')
##############################################################################################################################

class StartingActions(Enum):
    LAUNCH_PROGRAM: str = "Launching program..."
    ADD_DATABASE_PATH: str = "Adding database path..."
    CREATE_DB_LOCATION: str = "Creating db_location.json..."
    EXIT_WITHOUT_SETUP: str = "Exiting application without setting up a new database."

def main(db_path: str = None) -> None:
    MainMenu.print_menu(self=True)
    action = int(input("Select an option: ").strip())
    match action:
        case MainMenu.ADD_TRANSACTION.value:
            clogger.info("Add Transaction selected.")
            add_trasaction()
        case MainMenu.VIEW_TRANSACTIONS.value:
            print("View Transactions selected.")
        case MainMenu.VIEW_BALANCE.value:
            print("View Balance selected.")
        case MainMenu.VIEW_HISTORY.value:
            print("View History selected.")
        case MainMenu.MODIFY_BUDGET.value:
            print("Modify Budget selected.")
        case MainMenu.MODIFY_CATEGORIES.value:
            print("Modify Categories selected.")
        case MainMenu.AUTOMATION_FEATURES.value:
            print("Automation Features selected. (WIP)")
        case MainMenu.EXIT.value:
            print("Exiting application.")

def add_trasaction() -> None:
    payload = None #Instantiate a class from db_schema.py to hold the transaction data
    ui = iter(AddTransaction())
    print(next(ui))
    categories = next(ui)  # Get the categories dictionary
    for category, prompt in categories.items():
        print(f"{prompt} {category}")
    action = int(input("Select a category by number: ").strip())
    selected_category = list(categories.keys())[action - 1] if 0 < action <= len(categories) else None
    if selected_category:
        clogger.info(f"User selected category: {selected_category}")
        # Add category to payload object
    amount = input(next(ui)).strip()
    #TODO: If NaN, try stipping the first character (likely a $ sign), then convert to float .2f
    clogger.info(f"User entered amount: {amount}")
    description = input(next(ui)).strip()
    if description:
        clogger.info(f"User entered description: {description}")
    else:
        clogger.info("User did not provide a description, using default.")
    # TODO: Import datetime
    date_input = input(next(ui)).strip()
    if date_input:
        clogger.info(f"User entered date: {date_input}")
    else:
        clogger.info("User did not provide a date, using today's date.")
    # Send payload to db_relay.py to add the transaction 

def existence_check() -> None:
    """
    Checks if the database exists by looking for the db_location.json file then tells take_starting_action how to proceed.
    If the file exists and contains a valid path, it tells the take_starting_action function to launch the program.
    """
    existence, db_path = db.check_database_exists()
    if existence and db_path != "None":
        # db_location.json exists and it's database_path is valid
        clogger.info("Database found.")
        clogger.info(f"Current database: {Path(db_path).name}.")
        take_starting_action(StartingActions.LAUNCH_PROGRAM, Path(db_path))
    elif existence:
        # db_location.json exists but it's database_path is "None" or invalid
        clogger.warning("Database location not set or is invalid.")
        clogger.info(f"Current database path is {db_path}.")
        take_action = input("Do you want to specify the path? (yes/no): ").strip().lower()
        if take_action not in ["yes", "y"]:
            take_starting_action(StartingActions.EXIT_WITHOUT_SETUP, None)
        db_path = input("Input the full path to your database file: ").strip()
        take_starting_action(StartingActions.ADD_DATABASE_PATH, Path(db_path))
    else:
        # db_location.json does not exist or is invalid
        clogger.error("db_location.json file not found or invalid.")
        take_action = input("Do you already have a database file? (yes/no): ").strip().lower()
        if take_action in ['yes', 'y']:
            db_path = input("Please provide path to your database file: ").strip()
            take_starting_action(StartingActions.ADD_DATABASE_PATH, Path(db_path))
        else:
            take_action = input("Do you want to create a new database? (yes/no): ").strip().lower()
            if take_action in ['yes', 'y']:
                db_path = input("Please provide the path where you want to create the new database file: ").strip()
                take_starting_action(StartingActions.CREATE_DB_LOCATION, Path(db_path))
            else:
                clogger.info("User chose not to set up a new database.")
                take_starting_action(StartingActions.EXIT_WITHOUT_SETUP, None)
        
def take_starting_action(action: StartingActions, db_path) -> None:
    """
    Executes the action based on the StartingActions enum.
    """
    if action == StartingActions.LAUNCH_PROGRAM:
        print(f"{action.value}")
        main(db_path)
    elif action == StartingActions.ADD_DATABASE_PATH:
        print(f"{action.value}")
        db.setup_database(db_path, json_exists=True)
    elif action == StartingActions.CREATE_DB_LOCATION:
        print(f"{action.value}")
        db.create_db_location(db_path)
    elif action == StartingActions.EXIT_WITHOUT_SETUP:
        print(f"{action.value}")
        sys.exit(0)
    else:
        clogger.error("Invalid action specified.")

if __name__ == "__main__":
    # Check for database existence and take appropriate action
    existence_check()
