db_list = [
    "Grocery",
    "Medical",
    "Pet",
    "Restaurants",
    "Drinks",
    "Entertainment",
    "Shopping",
    "Transportation",
    "Subscriptions"
]
class db_payload:
    def __init__(self, table_name: str, cost: float, description: str = "", date: str = ""):
        """
        Initializes a database payload object with the necessary fields for a transaction.
        
        :param table_name: The name of the budget category table.
        :param cost: The cost of the transaction.
        :param description: A description of the transaction (optional).
        :param date: The date of the transaction (user defined or current date).
        """
        self.table_name = table_name
        self.cost = cost
        self.description = description
        self.date = date
        self.pseudo_hash_id = self.get_psuedo_hash(self.table_name, self.cost, self.date)

    def get_psuedo_hash(table_name: str, cost: float, date: str) -> int:
        """
        Generates a value semi-unique value that can be used to index specific transactions.
        XXXYYYZZZZ:
            XXX represents the table; 100 == ALL, Others are index of db_list * 100,000
            YYY represents the cost; 001 == $0 - $10, 020 = $200 - $219... 
            ZZZZ represents days since the creation of the database, 
                9999 states transaction occured before db creation and user chose to not use 0000
        Examples with db creation of 2025-04-10:
            Grocery transaction of $50 on 2025-05-11: 1010050031
            Amazon purchase of $219 on 2025-04-09 (input == "N" (don't use creation date)): 1070219999
            Code to search ALL transaction of < $10 on 2026-04-10: 1000010365
        """
        # TODO: Convert table_name to (index + 1) * 100000
        # TODO: Convert cost to a 3 digit value based on ranges
        # TODO: Convert date to a integer representing delta between db creation and transaction date
        pass
        return None  # Placeholder for the actual hash generation logic

def generate_archive_filename(creation_date) -> str:
    """
    Keeps the archive filename consistent with the database creation date.
    """
    creation_date = creation_date.replace('-', '_')
    archive_filename = f"db_{creation_date}.json"
    return archive_filename

if __name__ == "__main__":
    # Example usage
    transaction = db_payload(table_name="Grocery", cost="50.00", description="Weekly groceries", date="2023-10-01")
    print(f"Transaction created: {transaction.table_name}, Cost: {transaction.cost}, Description: {transaction.description}, Date: {transaction.date}")
