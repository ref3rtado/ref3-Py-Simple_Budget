from enum import Enum, auto

class MainMenuOptions(Enum):
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
    AUTOMATION_FEATURES = (7, "WIP Automation Features")
    EXIT = (8, "Exit the application")

    def print_menu(self):
        """ 
        Prints the main menu options to the console.
        """
        print(f'{"*" * 40}')
        for option in MainMenuOptions:
            print(f"{option.value}. {option.description}")
        print(f'{"*" * 40}\n')