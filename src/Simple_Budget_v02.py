
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
        i += 1
        main_ui.display_main_menu()
        main_ui.set_user_selection()
        execute_selection(main_ui.user_selection.name, db_path, archive_path)

def execute_selection(option, db_path, archive_path):
    # match/case here
    pass

if __name__ == "__main__":
    pass
