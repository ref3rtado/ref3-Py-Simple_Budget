## Main Script for Simple Budget Application ##
##############################################################################################################################

import database.db_relay as db
import logging
import sys
from pathlib import Path
from enum import Enum
from datetime import date
import json
from schema.ui_prompts import MainMenuOptions as MainMenu
from schema.ui_prompts import add_transaction_ui_flow as AddTransaction
from schema.ui_prompts import RotateDB_UI as RotateUI
from schema.ui_prompts import SetBudgetUI
from schema.db_schema import db_payload as db_payload


##############################################################################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="SimpleBudgetLogger", level=logging.DEBUG)
flogger = setup_logging(name="SimpleBudget", level=logging.DEBUG, log_file='Simple_Budget_Log.log')
##############################################################################################################################


class StartingActions(Enum):
    LAUNCH_PROGRAM: str = "Launching program..."
    ADD_PATH_TO_JSON: str = "Adding path to db_location.json..."
    CREATE_DB_LOCATION: str = "Creating db_location.json..."
    CREATE_DB: str = "Creating new database at specified path..."
    EXIT_WITHOUT_SETUP: str = "Exiting application without setting up a new database."

def take_starting_action(action: StartingActions, db_path, archive_path) -> None:
    """
    Executes the action based on the StartingActions enum.
    """
    if action == StartingActions.LAUNCH_PROGRAM:
        print(f"{action.value}")
        main(db_path)
    elif action == StartingActions.ADD_PATH_TO_JSON:
        print(f"{action.value}")
        db.setup_location_json(db_path, archive_path)
    elif action == StartingActions.CREATE_DB_LOCATION:
        print(f"{action.value}")
        db.create_db_location(db_path)
    elif action == StartingActions.CREATE_DB:
        print(f"{action.value}")
        db.setup_database(db_path, location_exists=True)
    elif action == StartingActions.EXIT_WITHOUT_SETUP:
        print(f"{action.value}")
        sys.exit(0)
    else:
        clogger.error("Invalid action specified.")


def existence_check() -> None:
    """
    #TODO: Refactor using ui_prompts.py
    Checks if the database exists by looking for the db_location.json file then tells take_starting_action how to proceed.
    If the file exists and contains a valid path, it tells the take_starting_action function to launch the program.
    """
    db_path, archive_path = db.check_database_exists()
    if db_path == "None":
        take_action = input(f'Database path hasn\'t been setup yet. Do you want to specify the path? (yes/no): ').strip().lower()
        if take_action in ['yes', 'y']:
            db_path = input("Enter the path to the database file: ").strip()
            action = StartingActions.ADD_PATH_TO_JSON
            if archive_path == "None":
                take_action = input(f'Archive directory not specified. Would you like to enter a path?(yes/no): ').strip().lower()
                if take_action in ['yes', 'y']:
                    archive_path = input("Enter the path to the archive folder: ").strip()
            take_starting_action(action, db_path, archive_path)
    if not archive_path or archive_path == "None":
        take_action = input(f'Archive directory not specified. Would you like to enter a path?(yes/no): ').strip().lower()
        if take_action in ['yes', 'y']:
            archive_path =  input("Enter the path to the archive folder: ").strip()
            action = StartingActions.ADD_PATH_TO_JSON
            take_starting_action(action, db_path, archive_path)
    main(db_path, archive_path)


def main(db_path: str = None, archive_path: str = None) -> None:
    MainMenu.print_menu(self=True)
    action = int(input("Select an option: ").strip())
    match action:
        case MainMenu.ADD_TRANSACTION.value:
            clogger.info("Add Transaction selected.")
            add_trasaction(db_path)
        case MainMenu.VIEW_TRANSACTIONS.value:
            print("View Transactions selected.")
        case MainMenu.VIEW_BALANCE.value:
            print("View Balance selected.")
        case MainMenu.VIEW_HISTORY.value:
            print("View History selected.")
        case MainMenu.MODIFY_BUDGET.value:          
            print("Modify Budget selected.")
            set_category_budget(db_path)
        case MainMenu.MODIFY_CATEGORIES.value:
            print("Modify Categories selected.")
        case MainMenu.ROTATE_DB.value:
            print("Rotate Database selected.")
            rotate_database(db_path, archive_path)
        case MainMenu.AUTOMATION_FEATURES.value:
            print("Automation Features selected. (WIP)")
        case MainMenu.EXIT.value:
            print("Exiting application.")



def add_trasaction(db_path) -> None:
    # TODO: Add input validation | Check out pydantic
    # TODO: If NaN, try stipping the first character (likely a $ sign), then convert to float .2f
    # TODO: After setting up the per-category budget, add the remaining category budget to print out.
    ui = iter(AddTransaction(db_path))
    print(next(ui))
    categories = next(ui)  # Get the categories dictionary
    for category, prompt in categories.items():
        print(f"{prompt} {category}")
    action = int(input("Select a category by number: ").strip())
    selected_category = list(categories.keys())[action - 1] if 0 < action <= len(categories) else None
    if selected_category:
        clogger.info(f"\nUser selected category: {selected_category}")
        # Add category to payload object
    amount = input(next(ui)).strip()    
    clogger.info(f"User entered amount: {amount}")
    payload = db_payload(table_name=selected_category, cost=float(amount))
    description = input(next(ui)).strip()
    if description:
        clogger.info(f"\nUser entered description: {description}")
        payload.description = description
    else:
        clogger.info("\nUser did not provide a description, using default.")
    date_input = input(next(ui)).strip()
    if date_input:
        clogger.info(f"\nUser entered date: {date_input}")
    else:
        date_input = date.today().isoformat()
        clogger.info("\nUser did not provide a date, using today's date.")
    payload.date = date_input
    clogger.debug(f"\nPayload created: {payload.__dict__}")
    # Send payload to db_relay.py to add the transaction 
    db.add_transaction(payload, db_path)
    cur_total_budget, cur_category_budget, remaining_total, category_spent = db.get_current_budget_stats(db_path, selected_category)
    summary = next(ui)
    print(summary.format(
        remaining_budget=remaining_total, 
        table=selected_category,
        category_budget = cur_category_budget,
        category_total = category_spent))


def rotate_database(db_path, archive_path) -> None:
    """
    Rotates the database by archiving the current one and creating a new one.
    """
    ui = RotateUI
    print(ui.START.value)
    clogger.debug(f"Database path: {db_path}, Archive path: {archive_path}")
    if archive_path == "None":
        print("An archive folder is required but not specified.")
        take_action = input(ui.FOLDER_MISSING.value).strip().lower()
        if take_action in ['yes', 'y']:
            archive_path = input(ui.GET_USER_PATH.value).strip()
            db.setup_location_json(db_path=db_path, archive_path=archive_path)
            db_path, archive_path = db.rotate_database(db_path, archive_path)
            print(ui.FOLDER_CREATED.value.format(archive_path=archive_path))
        else:
            clogger.info("User chose not to create an archive folder.")
            return
    take_action = input(ui.CONFIRM_ROTATION.value).strip().lower()
    if take_action in ['yes', 'y']:
        db.rotate_database(db_path, archive_path)

def set_category_budget(db_path):
    ui = SetBudgetUI(db_path)
    action = input(ui.master_prompt)
    print(ui.total_budget_as_slave(action))
    action = "y"
    while action in ["y", "Y"]:
        action = ui.get_table_from_user()
    ui.get_total_budget()
    ui.print_pending_mods()
    pending_budgets = ui.get_table_budget_dict()
    pass


if __name__ == "__main__":
    # Check for database existence and take appropriate action
    existence_check()

