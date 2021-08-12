import re
import os
import pandas as pd
from os import path
from common.constants import *
from datetime import datetime
from app.utils import to_snake
from transaction_data_tools.data_setup_utils import update_raw_transactions_file

MINT_SCHEMA = [
    "Date",
    "Description",
    "Original Description",
    "Amount",
    "Transaction Type",
    "Category",
    "Account Name",
]


def get_filename(downloads):
    """identify filename of most recent mint download"""
    mint_regex = r"transactions(\s\((\d+)\))?\.csv"

    # get all mint downloads
    mint_downloads = []
    for d in downloads:
        match = re.match(mint_regex, d)
        if match:
            if match.group(2):
                mint_downloads.append(int(match.group(2)))

    if len(mint_downloads) == 0:
        return "transactions.csv"
    elif len(mint_downloads) > 0:
        max_ind = max([x for x in mint_downloads if x])
        return f"transactions ({max_ind}).csv"


def update(downloads) -> str:
    logs = "\n\nUpdating mint transactions".upper()
    logs += update_raw_transactions_file(
        PATH_TO_MINT, PATH_TO_DOWNLOADS + get_filename(downloads), MINT_SCHEMA
    )
    return logs


def load_trans() -> pd.DataFrame:
    """Load raw mint transactions"""
    assert os.path.exists(PATH_TO_MINT)

    df = pd.read_csv(PATH_TO_MINT)
    df.columns = [to_snake(col) for col in df.columns]

    # remove repeated white space characters
    df['original_description'] = df['original_description'].apply(lambda txt: ' '.join(txt.split()))

    # group by all values to aggregate duplicate transactions
    group_keys = RAW_TRANSACT_SCHEMA.copy()
    group_keys.remove("amount")
    group_df = df.groupby(group_keys, as_index=False).amount.sum()

    # remove amzn and auth transactions
    # basically transactions we just want to ignore completely
    def is_false_transaction(descr) -> bool:
        substrings = ["amzn", "amazon", "auth :"]
        for s in substrings:
            if s in descr.lower():
                return True
        return False

    group_df = group_df[~group_df["original_description"].apply(is_false_transaction)]
    group_df["amount"] = group_df["amount"].round(2)
    group_df["date"] = group_df["date"].apply(lambda x: pd.to_datetime(x).date())

    return group_df[RAW_TRANSACT_SCHEMA]
