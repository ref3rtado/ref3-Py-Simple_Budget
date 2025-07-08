#TODO: Check for existence of db_location.json file
###### If not present, prompt user to create it, then use the specified path to create the database
#TODO: Import tinyDB 
##############################################################################################################################
from tinydb import TinyDB, Query as db
import json
import logging
import sys
from pathlib import Path
from typing import Union
##############################################################################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="db_relay_logger", level=logging.INFO)
flogger = setup_logging(name="db_relay", level=logging.DEBUG, log_file='Simple_Budget_Log.log')
##############################################################################################################################

def check_database_exists() -> Union[bool, str]:
    """
    Checks if the database exists by looking for the db_location.json file.
    If the file exists and contains a valid path, returns the path as a string.
    If the file does not exist or the path is "None" returns False.
    """
    p = Path(__file__).parent.resolve()
    json_path = p.joinpath('db_location.json')
    clogger.info(json_path)
    try:
        with open(json_path, 'r') as f:
            db_info = json.load(f)
            db_path = db_info.get('database_path')
            clogger.info(f"Database path from json: {db_path}")
            if Path(db_path).exists():
                return True, db_path, True 
            else:
                raise ValueError("Unable to locate database. The Database path could be invalid or the file does not exist.")
    except FileNotFoundError:
        clogger.error("db_location.json file not found. ")
        flogger.exception("FileNotFoundError: db_location.json not found.")
        return False, "None", False,
    except ValueError as ve:
        clogger.error(f"ValueError: {ve}")
        flogger.exception(f"ValueError: {ve}")
        return True, db_path if db_path else "None", False


def setup_database(db_path=None, location_exists=False) -> None:
    """
    Sets up or creates the dabase path in db_location.json.
    
    """
    p = Path(__file__).parent.resolve()
    json_path = p.joinpath('db_location.json')
    if location_exists:
        with open(json_path, 'w') as f:
            json.dump({'database_path': str(db_path)}, f, indent=4)
        print("Added path: ", db_path)
    else:
        # Create the json file with the specified path
        with open(json_path, 'w') as f:
            json.dump({'database_path': str(db_path)}, f, indent=4)
        print("Created db_location.json and added path: ", db_path)
    TinyDB(db_path)
        