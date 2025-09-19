from pathlib import Path
from tinydb import TinyDB, Query
from tinydb import operations as DBOper
import logging

###############################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="db_schema", level=logging.DEBUG)
###############################################################################

class DatabaseInfo:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.tables: list = []
        self.accounts = []
        self.creation_date: str = ''
        self.total_budget: float = 0.0

        with TinyDB(db_path) as db:
            self.tables = sorted(db.tables())
            metadata_table = db.table("metadata")
            self.creation_date = metadata_table.get(doc_id=1)["creation_date"]
            self.total_budget = metadata_table.get(doc_id=1)["total_budget"]
            self.accounts = metadata_table.get(doc_id=1)["accounts"]
            if self.accounts != None:
                self.accounts = sorted(self.accounts)
            
    
    def update_info_object(self):
        with TinyDB(self.db_path) as db:
            self.tables = sorted(db.tables())
            metadata_table = db.table("metadata")
            self.creation_date = metadata_table.get(doc_id=1)["creation_date"]
            self.total_budget = metadata_table.get(doc_id=1)["total_budget"]
            self.accounts = metadata_table.get(doc_id=1)["accounts"]
            if self.accounts != None:
                self.accounts = sorted(self.accounts)
            


def create_db(db_path: Path, db_properties: dict) -> None:
    TinyDB.default_table_name = "metadata"
    with TinyDB(
        db_path,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
    ) as db:
        metadata_properties = {
            "creation_date": db_properties["creation_date"],
            "total_budget": db_properties["total_budget"],
            "total_spent": db_properties["total_spent"],
            "accounts": db_properties["accounts"]
        }
        db.insert(metadata_properties)
        db_tables = db_properties["tables"]
        for table in db_tables:
            current_table = db.table(table)
            current_table.insert({
                "table_name": table,
                "category_budget": None,
                "total_spent": 0.0
            })

def insert_transaction(db_path: Path, payload: dict) -> dict:
    category, transaction = payload
    cost = transaction["cost"]
    response = {}
    with TinyDB(
        db_path,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
        ) as db:
        category_table = db.table(category)
        category_budget = category_table.get(doc_id=1)["category_budget"]
        clogger.debug(f"PRE INSERT:{category} budget: {category_budget}")        
        category_table.insert(transaction)
        clogger.debug(f"POST INSERT:{category} budget: {category_budget}")
        category_table.update(DBOper.add("total_spent", cost), doc_ids=[1])
        response["cat_total_spent"] = (
            category_table.get(doc_id=1)["total_spent"]
            )
        if category_budget is not None:
            updated_cat_budget = category_budget - cost
            category_table.update(
                {'category_budget': updated_cat_budget}, doc_ids=[1]
                )
            response['category_budget'] = updated_cat_budget
        else:
            response['category_budget'] = None
        metadata = db.table('metadata')
        if metadata.get(doc_id=1)["total_budget"] is not None:
            metadata.update(DBOper.subtract("total_budget", cost), doc_ids=[1])           
            response["total_budget"] = metadata.get(doc_id=1)["total_budget"]
        else:
            response["total_budget"] = None
        metadata.update(DBOper.add("total_spent", cost), doc_ids=[1])
        response["total_spent"] = metadata.get(doc_id=1)["total_spent"]
        
    return response

def add_account(db_path, account) -> bool:
    if not account: #User passed an empty string
        return False
    with TinyDB(
        db_path,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
        ) as db:
        metadata = db.table("metadata")
        acct_metadata = metadata.get(doc_id=1)
        cur_accounts = set((acct_metadata.get("accounts") or []))
        if account in cur_accounts:
            return False
        acct_payload = (
            sorted(cur_accounts.add(account)) if cur_accounts else [account]
        )
        metadata.update({"accounts": acct_payload}, doc_ids=[1])
    return True