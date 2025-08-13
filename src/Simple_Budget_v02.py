
import logging
from pathlib import Path
from datetime import date
#import database.db_relay as db
import src.User_Interface as UI

###############################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="SimpleBudget", level=logging.DEBUG)
###############################################################################

def main():
    startup_sequence()
    
def startup_sequence(test_cfg=None) -> tuple:
    startup = UI.StartupSequence(test_cfg)
    startup.check_location_json()
    db_path, archive_path = startup.get_paths()
    if db_path == None:
        startup.set_paths()
        db_path, archive_path = startup.get_paths()
    startup.validate_path(db_path, archive_path)

if __name__ == "__main__":
    pass
