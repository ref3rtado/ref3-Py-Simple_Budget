
import logging
from pathlib import Path
from datetime import date
import src.User_Interface as UI

###############################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="SimpleBudget", level=logging.DEBUG)
###############################################################################

def main():
    db_path, archive_path = startup_sequence()
    clogger.debug(f'Startup completed. Current paths: \n' \
                  f'Database path: {db_path} \n' \
                  f'Archive path: {archive_path} \n')
    main_menu(db_path, archive_path)
    
def startup_sequence(test_cfg=None) -> tuple:
    startup = UI.StartupSequence(test_cfg)
    startup.check_location_json()
    db_path, archive_path = startup.get_paths()
    if db_path == None:
        startup.set_paths()
        db_path, archive_path = startup.get_paths()
    try:
        startup.validate_paths()
    except FileNotFoundError as err:
        print(err, "\n")
        startup.create_first_db()
    return db_path, archive_path

def main_menu(db_path, archive_path):
    main_ui = UI.MainMenu()
    options = main_ui.menu_options
    i = 0
    while main_ui.user_selection != options.EXIT and i < 5:
        #TODO: Delete i loop condition | Current use prevent infinite loops while deving
        i += 1
        main_ui.display_main_menu()
        main_ui.set_user_selection()
        execute_selection(main_ui, db_path, archive_path)

def execute_selection(main_ui, db_path, archive_path):
    selection = main_ui.menu_options
    match main_ui.user_selection:
        case selection.ADD_TRANSACTION:
            clogger.debug("Add Transaction selected")
            add_transaction(db_path)
        case selection.VIEW_TRANSACTIONS:
            clogger.debug("View transaction selected")
            view_transactions(db_path)
        case selection.VIEW_BALANCE:
            clogger.debug("View budget selected.")
            view_balance(db_path)
        case selection.VIEW_HISTORY:
            clogger.debug("View history selected.")
            view_history(db_path, archive_path)
        case selection.MODIFY_BUDGET:
            clogger.debug("Modify budget selected.")
            modify_budget(db_path)
        case selection.MODIFY_CATEGORIES:
            clogger.debug("Modify categories selected.")
            modify_categories(db_path)
        case selection.AUTOMATION_FEATURES:
            clogger.debug("PLACEHODER")
            automation_features(db_path)
        case selection.ROTATE_DB:
            clogger.debug("Rotate database selected.")
            rotate_database(db_path, archive_path)
        case selection.EXIT:
            clogger.debug("Exit selected. Exiting program.")
            print("Exiting program...")
        case _:
            print("Invalid selection, try again.")


def add_transaction(db_path):
    ui = UI.AddTransactionUI(db_path)
    ui.set_category()
    ui.set_account()
    ui.set_transaction_info()
    ui.insert_transaction()

def view_transactions(db_path):
    pass

def view_balance(db_path):
    pass

def view_history(db_path, archive_path):
    pass

def modify_budget(db_path):
    pass

def modify_categories(db_path):
    pass

def automation_features(db_path):
    pass

def rotate_database(db_path, archive_path):
    pass

if __name__ == "__main__":
    pass
