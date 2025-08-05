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

def get_current_tables_new(db_path):
    table_options = {}
    tables = None
    with TinyDB(db_path) as db:
        table_set = db.tables()
        tables = sorted(list(table_set))
    for i, table in enumerate(tables):
        if table == "All_Tables":
            continue
        table_options[i] = table
    print(table_options)
    return table_options

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
        '\n\n--Remaining budget-- \nRemaining budget: {remaining_budget} \n{table} budget: {category_budget}\nTotal {table} spent: {category_total}']
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

class SetBudgetUI:
    def __init__(self,  db_path):
        print("-SET BUDGETS-")
        self.db_path = db_path
        self.master_prompt = "Should the overall budget be the sum of all category budgets? y/n/q"
        self.select_tables_prompt = "Select a category to set the budget for: "
        self.master = False
        self.table_options = get_current_tables_new(self.db_path)
        self.modifications_to_push = {}        
        pass
    
    def total_budget_as_slave(self, action):
        match action:
            case "q" | "Q":
                print("Returning to main menu...")
                return # may need different method to quit
            case "y" | "Y":
                self.master = True
                return "Total budget will be determined by sum of all categories."
            case "n" | "N":
                return "Total budget will be independent of category budgets."
            case _:
                return "Invalid input. Using default option [FALSE]."
    
    def get_table_from_user(self) -> str:
        print('\n', '*' * 20)
        for key, value in self.table_options.items():
            print(f'{key}: {value}')
        selected_option = int(input("\nSelect a table to set the budget for:"))
        selected_table = self.table_options[selected_option]
        user_budget = float(input(f"\nEnter the budget for {selected_table}: "))
        self.modifications_to_push[selected_table] = user_budget
        action = input("Set the budget for another category? y/n/q: ")
        return action
    
    def print_pending_mods(self):
        print('\n--Budgets to be modified--')
        print(self.modifications_to_push)
    
    def get_total_budget(self):
        total_budget = 0.0
        if self.master:
            for budget in self.modifications_to_push.values():
                total_budget += budget
            print(f'Total budget determined by category sum: {total_budget}')
            self.modifications_to_push["All_Tables"] = total_budget
        else:
            action = input("Would you like to set a independent overall budget? (y/n): ")
            if action in ("y, Y"):
                total_budget = float(input("Enter the overall budget: "))
                self.modifications_to_push["All_Tables"] = total_budget
    
    def get_table_budget_dict(self) -> dict:
        return self.modifications_to_push