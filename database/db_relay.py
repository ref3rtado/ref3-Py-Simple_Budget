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
    def __init__(self, db_path: str, tables: list = db_list, total_budget: float = 0.0):
        """
        Initializes a new database at the specified path.
        Most often used when the database is rotated.        
        :param tables: Default tables hardcoded in db_schema.py. User can pass a list of tables to override the defaults.
        """
        self.creation_date = date.today().isoformat()
        self.total_budget = total_budget
        self.tables = tables
        self.db_path = db_path
        
        db = TinyDB(self.db_path, sort_keys=True, indent=4, separators=(',', ': '))
        db.default_table_name = 'All_Tables'
        db.insert({'creation_date': self.creation_date})
        db.insert({'total_budget': self.total_budget})
        for table in self.tables:
            # Create a new table for each category
            current_table = db.table(table)
            current_table.insert({   
                'table_name': table,
                'category budget': 0.0
            })
            clogger.info(f"Table '{table}' created in database at {self.db_path}")


def check_database_exists() -> str:
    """
    Checks if the database exists by looking for the db_location.json file.
    If the file exists and contains a valid path, returns the path as a string.
    If the file does not exist or the path is "None" returns False.
    """
    location_json_path = Path(__file__).parent.joinpath('db_location.json').resolve()
    clogger.debug(f"Checking for db_location.json at: {location_json_path}")
    db_path = None
    archive_path = None
    try:
        with open(location_json_path, 'r') as f:
            locations = json.load(f)
            db_path = locations.get('database_path')
            archive_path = locations.get('archive_path')
            clogger.debug(f"Database path from json: {db_path}")
            clogger.debug(f"Archive path from json: {archive_path}")
            if not Path(db_path).exists() or db_path == "None":
                print("Path to database is invalid or the database does not exist.")
                return db_path, archive_path
    except FileNotFoundError:
        clogger.error("db_location.json file not found. ")
        print("Setting up a json file to store database path...")
        setup_location_json()
        db_path, archive_path = setup_database(location_json_path)
    return db_path, archive_path

def setup_database(db_path, archive_path) -> str:
    """
    Sets up or creates the dabase path in db_location.json.
    """
    if db_path == "None" or not Path(db_path).exists():
        clogger.debug(f"Database path is invalid or does not exist: {db_path}")
        db_path = input("Please enter a valid path to the database file.")
    if archive_path == "None" or not Path(archive_path).exists():
        clogger.debug(f"Archive path is invalid or does not exist: {archive_path}")
        archive_path = input("Please enter a valid path to the archive folder.")
        if not Path(archive_path).exists():
            Path(archive_path).mkdir(parents=True, exist_ok=True)
            clogger.info(f"Archive folder created at: {archive_path}")
    db_path = Path(db_path).resolve()
    archive_path = Path(archive_path).resolve()
    location_json_path = Path(__file__).parent.joinpath('db_location.json').resolve()
    with open(location_json_path, 'w') as f:
        json.dump({'database_path': str(db_path), 'archive_path': str(archive_path)}, f, indent=4)
    if not db_path.exists():
        clogger.debug("database file does not exist, creating a new one.")
        InitializeNewDatabase(db_path, tables=db_list)
    return db_path, archive_path

def setup_location_json(db_path: str = None, archive_path: str = None) -> None:
    location_json_path = Path(__file__).parent.joinpath('db_location.json').resolve()
    with open(location_json_path, 'w') as f:
        json.dump({"database_path": str(db_path), "archive_path": str(archive_path)}, f, indent=4)

def rotate_database(db_path: str=None, archive_path: str=None) -> None:
    clogger.debug(f"Locations: {locations}")
    clogger.debug(f"Archive path: {archive_path}")
    clogger.debug(f"Database path: {db_path}")
    db_path = Path(db_path).resolve()
    archive_path = Path(archive_path).resolve()
    if not archive_path.exists():
        archive_path.mkdir(parents=True, exist_ok=True)
        clogger.info(f"Archive folder created at: {archive_path}")
    
    # Move the current database to the archive folder
    clogger.debug(f"Moving database from {db_path} to {archive_path}")
    current_db = TinyDB(db_path)
    with current_db as db:
        default_table = current_db.table('All_Tables')
        creation_date = default_table.get(doc_id=1).get('creation_date')
        creation_date = creation_date.replace('-', '_')
        archive_destination = archive_path.joinpath(f"db_{creation_date}.json")
        if archive_destination.exists():
            existing_file_name = archive_destination.stem
            if existing_file_name[-1] == ']':
                i = existing_file_name.rfind('[')
                new_file_name = f"{existing_file_name[:i]}[{int(existing_file_name[i+1:]) + 1}]"
                existing_file_name = new_file_name
            else:
                existing_file_name = f"{existing_file_name}[1]"
            archive_destination = archive_destination.with_name(existing_file_name + archive_destination.suffix)
        clogger.debug(f"Archive destination: {archive_destination}")
    shutil.move(str(db_path), str(archive_destination))
   
    # Create a new database
    setup_database(db_path=db_path, location_exists=True)

def add_transaction(payload: object, db_path: str) -> None:
    pass
