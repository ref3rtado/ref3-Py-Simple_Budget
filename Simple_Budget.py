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
from typing import Union

# Configure logging
clogger = db.setup_logging(name="SimpleBudgetLogger", level=logging.INFO)
clogger.info("Starting Simple Budget Application...")

def main(db_path: str = None) -> None:
    # Main program logic
    print("Welcome to the Simple Budget Application!")
    pass

def existence_check() -> Union[str, Path]:
    """
    Checks if the database exists by looking for the db_location.json file.
    If the file exists and contains a valid path, returns a path object.
    """
    existence, db_path = db.check_database_exists()
    if existence and db_path != "None":
        # db_location.json exists and it's database_path is valid
        clogger.info("Database found.")
        clogger.info(f"Current database {Path(db_path).name}.")
        return "Launching program...", Path(db_path)
    elif existence:
        # db_location.json exists but it's database_path is "None" or invalid
        clogger.warning("Database location not set or is invalid.")
        clogger.info(f"Current database path is {db_path}.")
        take_action = input("Do you want to specify the path? (yes/no): ").strip().lower()
        if take_action not in ["yes", "y"]:
            return "Exiting application without setting up a new database.", None
        db_path = input("Input the full path to your database file: ").strip()
        return "Adding database path...", Path(db_path).resolve()
    else:
        # db_location.json does not exist or is invalid
        clogger.error("db_location.json file not found or invalid.")
        take_action = input("Do you already have a database file? (yes/no): ").strip().lower()
        if take_action not in ['yes', 'y']:
            return "Exiting application without setting up a new database.", None
        db_path = input("Please provide path to your database file: ").strip()
        return "Creating db_location.json...", Path(db_path).resolve()

if __name__ == "__main__":
    # TODO: Decide if create db  function call should be here or in db_relay.py
    action, db_path = existence_check()
    starting_actions = {
        "Launching program...": lambda: main(db_path),
        "Adding database path...": lambda: db.setup_database(db_path, json_exists=True),
        "Creating db_location.json...": lambda: db.create_db_location(db_path),
        "Exiting application without setting up a new database.": lambda: sys.exit(0)
    }
    if action in starting_actions.keys():
        print(action)
        starting_actions[action]()