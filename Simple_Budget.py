## Main Script for Simple Budget Application ##
#TODO: Import db_relay module

#TODO: On startup, check if the database exists by talking to db_relay.py

#TODO: Print a welcome message, interaction menu, and prompt for user input
##Example: 1) Add Transaction | 2) Check Balance | 3) Modify Tables | 4) Exit
##On "1"
### Pull and enumerate the columns in the database, present as numbered options -- 1) Grocery, 2) Shopping, etc. 
#### On "1"
##### Prompt for amount, optional description, and date
###### On enter, print something like "Transaction added" /n "Current Balance: $X.XX"

##############################################################################################################################

import database.db_relay as db
import logging

# Configure logging
clogger = db.setup_logging(name="SimpleBudgetLogger", level=logging.INFO)
clogger.info("Starting Simple Budget Application...")

def main():
    # Main program logic
    pass

if __name__ == "__main__":
    # TODO: Decide if create db  function call should be here or in db_relay.py
    if db.check_database_exists():
        clogger.info("Database found.")
        main()
        pass
    else:
        clogger.error("Database not found.")
        # Get input to tell program how to proceed. 
        # Function to set up the database and create the database_location.json file
        pass
