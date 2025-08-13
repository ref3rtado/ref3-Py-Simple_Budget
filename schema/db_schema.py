from tinydb import TinyDB, Query
import logging
from pathlib import Path
from datetime import date

###############################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="db_schema", level=logging.DEBUG)
###############################################################################

class InitializeNewDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.creation_date = date.today().isoformat()
        self.tables = None
        self.total_budget = None
        self.total_spent = 0.0
    
    def set_default_tables(self):
        default_tables = [
            "Groceries",
            "Shopping",
            "Medical",
            "Pet",
            "Restaurants",
            "Drinks",
            "Entertainment",
            "Transportation",
            "Subscriptsion"
        ]
        self.tables = default_tables
    
    def set_custom_talbes(self, user_tables: list):
        """
        :param user_tables: list | Provide a comma separated list of tables
            to initialize the database with. 
        
        Table budgets are set at the main menu.
        """
        self.tables = user_tables
    
    def get_tables(self) -> list:
        return self.tables
    
    def use_old_settings(self):
        """
        Pull the settings from current db and reuse them for the new db. 
        Used for db rotation functionality.
        """
        # Get tables
        # Get total_budget
        # Set tables
        # Set total_budget
        pass
    
    def override_metadata(self, user_date=None, total_spent=None):
        """
        :param: user_date mm/dd/yyyy : Set custom creation date
        :param: total_spent: float | Change total_spent. WARNING:
            Can potentially cause problems with db operations.
        """
        self.creation_date = user_date
        self.total_spent = total_spent
    
    def create_database(self):
        if Path(self.db_path).exists():
            raise FileExistsError(f"ERROR: Database already exists at \
                                  {self.db_path} \n Please use the \
                                    rotate_db function from main menu.")
        TinyDB.default_table_name = "metadata"
        with TinyDB(
            self.db_path, 
            sort_keys=True, 
            indent=4,
            separators=(',', ': ')) as db:
            db.insert({
                'creation_date': self.creation_date,
                'total_budget': self.total_budget,
                'total_spent': self.total_spent
            })
            for table in self.talbes:
                current_table = db.table(table)
                current_table.insert({
                    'table_name': table,
                    'category_budget': None,
                    'total_spent': 0.0
                })
                clogger.debug(f'Table "{table}" created in database \
                              {self.db_path}')
        pass

