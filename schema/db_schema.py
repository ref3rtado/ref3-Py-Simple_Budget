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
        XXXYYYZZZ:
            XXX represents the table; 100 == ALL, Others are index of db_list * 10,000
            YYY represents the cost; 001 == $0 - $10, 020 = $200 - $219... 
            ZZZ represents a delta range between date of transaction and date of most recent db cycle.
                If the transaction occured before the last db cycle, it will be 
                400 + (years since cycle * 100) + months since cycle.
        Examples with last db cycle on 2025-04-10:
            Grocery transaction of $50 on 2025-04-11: 101005030
            Amazon purchase of $219 on 2025-04-09 (One day before cycle): 107021400
            Code to search ALL transaction of < $10 on 2025-04-11: 100001030
        """
        pass
        return None  # Placeholder for the actual hash generation logic

if __name__ == "__main__":
    # Example usage
    transaction = db_payload(table_name="Grocery", cost="50.00", description="Weekly groceries", date="2023-10-01")
    print(f"Transaction created: {transaction.table_name}, Cost: {transaction.cost}, Description: {transaction.description}, Date: {transaction.date}")
