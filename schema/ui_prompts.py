from tinydb import TinyDB, Query
from enum import Enum, auto
from datetime import date

class MainMenuOptions(Enum):
    '''
    An Enum class is used to define constant main menu options and the respective input that triggers them. 
    '''
    def __new__(cls, option, description):
        obj = object.__new__(cls)
        obj._value_ = option
        obj.description = description
        return obj
    ADD_TRANSACTION = (1, "Add a new transaction")
    VIEW_TRANSACTIONS = (2, "View recent transactions")
    VIEW_BALANCE = (3, "View remaining budget balance")
    VIEW_HISTORY = (4, "View historical balances")
    MODIFY_BUDGET = (5, "Modify budget limits")
    MODIFY_CATEGORIES = (6, "Add, rename, or remove budget categories")
    ROTATE_DB = (7, "Rotate database (Archive current db and create a new one)")
    AUTOMATION_FEATURES = (8, "PLACEHOLDER Automation Features")
    EXIT = (9, "Exit the application")

    def print_menu(self):
        """ 
        Prints the main menu options to the console.
        """
        print(f'{"*" * 40}')
        for option in MainMenuOptions:
            print(f"{option.value}. {option.description}")
        print(f'{"*" * 40}\n')

class RotateDB_UI(Enum):
    """
    UI PROMPTS
    Guides the user through the process of rotating the database.
    """
    # Check existence of archive folder path
    # If it exists, print path
    # Else, prompt user to create it
    START = "-ROTATE DB FILE-\nChecking for existing archive folder..."
    FOLDER_EXISTS = "Archive folder exists at: {archive_path}"
    FOLDER_MISSING = "Archive folder not specified. Would you like to specify and/or create a new archive location? (yes/no): "
    GET_USER_PATH = "Enter that path to store the archive: "
    FOLDER_CREATED = "Archive folder created at: {archive_path}"
    CONFIRM_ROTATION = "Continue with rotating the database? (yes/no): "

def get_current_tables(db_path, display_tables=False) -> dict:
    """
    Grabs the current tables from the database and returns them as a list.
    :param db_path: string of path to database
    :param display_tables: Boolean[Optional] True: print out list and return None, else return dict selector: table_name 
    """
    db = TinyDB(db_path)
    existing_tables = db.tables()
    table_dict = {}
    db.close()
    for i, category in enumerate(existing_tables, start=1):
        table_dict[category] = f'{i}. '
        if display_tables:
            print(f'{i}. {category}')
    if not display_tables:
        return table_dict

def add_transaction_ui_flow(db_path) -> list:  
    """
    Dynamic iterable [list{dict}].
    Guides the user through the process of adding a transaction.
    """
    add_transaction_flow = [
        "-CATEGORIES-",
        'Enter the cost of the trasaction | "q" to cancel: ',
        'Enter a description for the transaction (optional) | "q" to cancel: ',
        'Enter the date of the transaction (YYYY-MM-DD) or press Enter for today | "q" to cancel: ',
        '\n\n--Remaining budget-- \nTotal budget: {remaining_budget} \n{table} budget: {category}\nTotal {table} spent: {category_total}']
    categories = get_current_tables(db_path)
    add_transaction_flow.insert(1, categories)
    return add_transaction_flow

def set_table_budgets_ui(db_path) -> dict:
    """
    Walk through the process of setting individual budget limits per category.
    """
    current_tables = get_current_tables(db_path)
    table_budget_ui = {
        'control_total_budget': "Should the overall budget be the sum of all category budgets? y/n/q",
        'display tables': current_tables, 
        'select category': "Select the category to modify budget limit: ",
        'print_current_budget': "{category} | Current budget set at {cur_budget}",
        'enter_amount': "{category} | Enter budget: ",
        'budget_set': "{category}" | "Budget set.",
        'print_results':"""
                            --Current Budgets--
                            Sum of all categories: {category_sum}
                            Overall Budget: {total_budget}
                        """,
        # sum != overall budget?
    }
    return table_budget_ui





    