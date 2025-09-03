from pathlib import Path
from tinydb import TinyDB, Query
import logging

###############################################################################
from log.LogSetup import setup_logging
clogger = setup_logging(name="db_schema", level=logging.DEBUG)
###############################################################################

def create_db(db_path, db_properties) -> None:
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
            "total_spent": db_properties["total_spent"]
        }
        db.insert(metadata_properties)
        db_tables = db_properties["tables"]
        for table in db_tables:
            current_table = db.table(table)
            current_table.insert({
                "table_name": table,
                "cateogry_budget": None,
                "total_spent": 0.0
            })