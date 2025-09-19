import logging
from pathlib import Path
from datetime import date

###############################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="db_schema", level=logging.DEBUG)
###############################################################################

class InitializeNewDatabase:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.creation_date = date.today().isoformat()
        self.tables = None
        self.total_budget = None
        self.total_spent = 0.0
        self.accounts = None
    
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
            "Subscriptions"
        ]
        self.tables = default_tables
    
    def set_custom_tables(self, user_tables: list):
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
        :param: user_date yyyy/mm/dd : Set custom creation date
        :param: total_spent: float | Change total_spent. WARNING:
            Can potentially cause problems with db operations.
        """
        self.creation_date = user_date
        self.total_spent = total_spent
    
    def set_total_budget(self, user_budget: float):
        try:
            self.total_budget = float(user_budget)
        except TypeError as err:
            print(err)
            print("Total budget value must be a float.")
            print("Setting total budget to None")

    def get_db_properties(self) -> dict:
        return {
            "creation_date": self.creation_date,
            "tables": self.tables,
            "total_budget": self.total_budget,
            "total_spent": self.total_spent,
            "accounts": self.accounts
        }

class AddTransactionPayload:
    def __init__(
        self,
        qkadd=False, # Quick Add: Arg based CLI option
        category=None,
        cost: float=0.0,
        description: str = '',
        account: str = '',
        date: date = date.today().isoformat()
    ):
        self.category = category
        self.cost = cost
        self.description = description
        self.account = account
        self.date = date

        if qkadd:
            payload = {
                "table": self.category,
                "cost": self.cost,
                "description": self.description,
                "account": self.account,
                "date": self.date
            }
            clogger.debug(f'Quick Add payload created: {payload}')
            return payload
        
    def __str__(self):
        return (f'\nCategory: {self.category} \n' 
                f'Cost: {self.cost} \n' 
                f'Description: {self.description} \n'
                f'Account: {self.account} \n' 
                f'Date: {self.date} \n'
                )

    def get_payload(self) -> tuple:
        return (
            self.category, {
            "date": self.date,
            "cost": self.cost,
            "description": self.description,
            "account": self.account
        })