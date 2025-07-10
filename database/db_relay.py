#TODO: Check for existence of db_location.json file
###### If not present, prompt user to create it, then use the specified path to create the database
#TODO: Import tinyDB 
##############################################################################################################################
from tinydb import TinyDB, Query
import json
import logging
import sys
from pathlib import Path
from typing import Union
from datetime import date
from schema.db_schema import db_list
import schema.ui_prompts as ui
import shutil
##############################################################################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="db_relay_logger", level=logging.DEBUG)
flogger = setup_logging(name="db_relay", level=logging.DEBUG, log_file='Simple_Budget_Log.log')
##############################################################################################################################
class InitializeNewDatabase:
    def __init__(self, db_path: str, tables: list = db_list):
        """
        Initializes a new database at the specified path.
        Most often used when the database is rotated.        
        :param tables: Default tables hardcoded in db_schema.py. User can pass a list of tables to override the defaults.
        """
        self.creation_date = date.today().isoformat()
        self.tables = tables
        self.db_path = db_path
        
        db = TinyDB(self.db_path)
        db.insert({'creation_date': self.creation_date})
        for table in self.tables:
            # Create a new table for each category
            current_table = db.table(table)
            current_table.insert({   
                'table_name': table
            })
            clogger.info(f"Table '{table}' created in database at {self.db_path}")


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
    InitializeNewDatabase(db_path, tables=db_list)

def rotate_database(db_path: str=None, archive_path: str=None, add_path_to_json: str=None) -> None:
    locations = Path(__file__).parent.joinpath("db_location.json").resolve()
    clogger.debug(f"Locations: {locations}")
    clogger.debug(f"Archive path: {archive_path}")
    clogger.debug(f"Database path: {db_path}")

    if add_path_to_json:
        with open(locations, 'w') as f:
            json.dump({"database_path": str(db_path), "archive_path": str(add_path_to_json)}, f, indent=4)
            clogger.debug(f"Added archive path to db_location.json: {add_path_to_json}")
        with open(locations, 'r') as f:
            paths = json.load(f)
            db_path = paths.get('database_path')
            archive_path = paths.get('archive_path')
        archive_path = Path(archive_path).resolve()
        if not archive_path.exists():
            archive_path.mkdir(parents=True, exist_ok=True)
            clogger.info(f"Archive folder created at: {archive_path}")
            return db_path, archive_path

    if not db_path and not archive_path:
        clogger.debug(f"Locations file: {locations}")  
        with open(locations, 'r') as f:
            paths = json.load(f)
            db_path = paths.get('database_path')
            archive_path = paths.get('archive_path')
        clogger.info(db_path)
        clogger.info(archive_path)
        return db_path, archive_path
    
    db_path = Path(db_path).resolve()
    archive_path = Path(archive_path).resolve()
    if not archive_path.exists():
        archive_path.mkdir(parents=True, exist_ok=True)
        clogger.info(f"Archive folder created at: {archive_path}")
    
    # Move the current database to the archive folder
    clogger.debug(f"Moving database from {db_path} to {archive_path}")
    current_db = TinyDB(db_path)
    with current_db as db:
        default_table = current_db.table('_default')
        creation_date = default_table.get(doc_id=1).get('creation_date')
        creation_date = creation_date.replace('-', '_')
        archive_destination = archive_path.joinpath(f"db_{creation_date}.json")
    shutil.move(str(db_path), str(archive_destination))
    
    # Create a new database
    setup_database(db_path=db_path, location_exists=True)
