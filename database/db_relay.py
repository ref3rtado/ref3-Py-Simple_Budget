
##############################################################################################################################
from tinydb import TinyDB, Query
from tinydb.operations import subtract, add
import json
import logging
import sys
from pathlib import Path
from typing import Union
from datetime import date
from schema.db_schema import db_list as db_list
from schema.db_schema import db_payload as db_payload
import schema.db_schema as db_schema
import schema.ui_prompts as ui
import shutil


##############################################################################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="db_relay_logger", level=logging.DEBUG)
flogger = setup_logging(name="db_relay", level=logging.DEBUG, log_file='Simple_Budget_Log.log')
##############################################################################################################################


class InitializeNewDatabase:
    def __init__(self, db_path: str, tables: list = db_list, total_budget: float = 1000.0, custom_params = False, user_params: dict = {}):
        """
        Initializes a new database at the specified path.
        Most often used when the database is rotated.        
        :param tables: Default tables hardcoded in db_schema.py. User can pass a list of tables to override the defaults.
        :param custom_params: Boolean, if true check user_params dictionary 
        :param user_params: Dictionary that should contain {creation_date: str, total_budget: float}
        """
        self.creation_date = date.today().isoformat()
        self.total_budget = total_budget
        self.tables = tables
        self.db_path = db_path
        self.total_spent = 0.0

        if custom_params:
            self.creation_date = user_params['creation_date'] if user_params['creation_date'] else date.today().isoformat()
            self.total_budget = user_params['total_budget'] if user_params['total_budget'] else total_budget
        
        TinyDB.default_table_name = 'All_Tables'       

        db = TinyDB(self.db_path, sort_keys=True, indent=4, separators=(',', ': '))
        db.insert({'creation_date': self.creation_date})
        db.insert({'total_budget': self.total_budget})
        db.insert({'total_spent': self.total_spent})
        for table in self.tables:
            # Create a new table for each category
            current_table = db.table(table)
            current_table.insert({   
                'table_name': table,
                'category_budget': None,
                'total_spent' : 0.0
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


def get_paths() -> str:
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
            return db_path, archive_path
    except FileNotFoundError:
        clogger.error("db_location.json file not found. ")
        print("Setting up a json file to store database path...")
        setup_location_json()
        print("Configuration file created. You will need to enter the paths to continue.")
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
    clogger.debug(f'Adding db path: {db_path}')
    clogger.debug(f'Adding archive path: {archive_path}')
    with open(location_json_path, 'w') as f:
        json.dump({"database_path": str(db_path), "archive_path": str(archive_path)}, f, indent=4)


def rotate_database(db_path: str=None, archive_path: str=None, custom_params_for_new_db = {}) -> None:
    clogger.debug(f"Archive path: {archive_path}")
    clogger.debug(f"Database path: {db_path}")

    db_path = Path(db_path).resolve()
    archive_path = Path(archive_path).resolve()
    if not archive_path.exists():
        archive_path.mkdir(parents=True, exist_ok=True)
        clogger.error(f"Archive folder didn't exist, it has been created at: {archive_path}")
    
    # Move the current database to the archive folder
    clogger.debug(f"Moving database from {db_path} to {archive_path}")
    current_db = TinyDB(db_path)
    with current_db as db:
        default_table = current_db.table('All_Tables')
        if not default_table.contains(doc_id=1):
            clogger.error("Default table 'All_Tables' does not exist in the database.")
            return
        creation_date = default_table.get(doc_id=1).get('creation_date')
        archive_filename = db_schema.generate_archive_filename(creation_date)
        archive_destination = archive_path.joinpath(archive_filename)
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
    if custom_params_for_new_db:
        InitializeNewDatabase(db_path=db_path, tables=db_list, custom_params=True, user_params=custom_params_for_new_db)
    else:
        InitializeNewDatabase(db_path=db_path, tables=db_list)


def add_transaction(payload: object, db_path: str) -> None:
    #TODO: Create function to update and return budget totals.
    db = TinyDB(db_path, sort_keys=True, indent=4, separators=(',', ': '))
    payload_table = payload.get_table_name()
    try:
        db_table = db.table(payload_table)
    except Exception as table_err: 
        clogger.error(table_err)
        clogger.error(f"Could not grab the table'{payload_table}' from the database at {db_path}")
        return table_err
    else:
        clogger.debug(f'Got table name: {payload_table}')
    payload = payload.get_payload_data()
    clogger.debug(f'Payload to add: {payload}')
    try:
        db_table.insert(payload)
    except Exception as insert_err:
        clogger.error(insert_err)
        clogger.error(f"Could not add the payload to db {db_path}")
        return insert_err
    else:
        db_table.update(add("total_spent", float(payload["cost"])), doc_ids=[1])
    
    # Update the total budget and return the value
    all_tables = db.table("All_Tables")
    all_tables.update(subtract("total_budget", float(payload["cost"])), doc_ids=[2])
    new_total_budget = all_tables.all()[1].get("total_budget")
    clogger.debug(f'Updated total budget amount to: {new_total_budget}')


def get_current_budget_stats(db_path, table) -> tuple: 
    db = TinyDB(db_path, sort_keys=True, indent=4, separators=(',', ': '))
    all_tables = db.table("All_Tables")
    total_budget = all_tables.all()[1].get("total_budget")
    total_spent = all_tables.all()[2].get("total_spent")
    total_budget_remaining = total_budget - total_spent
    category_table = db.table(table)
    category_budget = category_table.get(doc_id=1)['category_budget']
    category_spent = category_table.get(doc_id=1)['total_spent']
    return total_budget, category_budget, total_budget_remaining, category_spent

def set_table_budgets(db_path, budget_dict):
    # connect to db with dbpath
    # get table object
    # update table's budget variable
    # Query() all docs with key "budget" and exist as docs inside the master table
        # If master True: add all values together and update the all_tables (category container) budget
    # Return tuple (total_budget, sum_of_tables)
    db = TinyDB(db_path, sort_keys=True, indent=4, separators=(',', ': '))
    for table_name, budget_value in budget_dict.items():
        table = db.table(table_name)
        if table_name == "All_Tables":
            table.update({"total_budget": budget_value}, doc_ids=[2])
        else:
            table.update({"category_budget": budget_value}, doc_ids=[1])
    db.close()