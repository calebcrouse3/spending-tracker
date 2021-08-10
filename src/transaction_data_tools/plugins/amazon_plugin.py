import re
from os import path
import pandas as pd
from common.constants import *
from app.utils import to_snake
from transaction_data_tools.data_setup_utils import update_raw_transactions_file

AMAZON_SCHEMA = [
    "Order Date",
    "Order ID",
    "Title",
    "Category",
    "Seller",
    "Item Total"
]


def get_filenames(downloads) -> str:
    """identify all amzn order histories"""
    amzn_regex = r"\d{2}-\w{3}-\d{4}_to_\d{2}-\w{3}-\d{4}(\s\((\d+)\))?\.csv"

    amzn_downloads = []
    for d in downloads:
        match = re.match(amzn_regex, d)
        if match:
            amzn_downloads.append(match.group())

    return amzn_downloads


def update(downloads) -> str:
    logs = "\n\nUpdating amazon records".upper()
    amazon_filenames = get_filenames(downloads)
    for file in amazon_filenames:
        logs += update_raw_transactions_file(
            PATH_TO_AMAZON, PATH_TO_DOWNLOADS + file, AMAZON_SCHEMA
        )
    return logs


def load_trans() -> pd.DataFrame:
    """Load raw amazon transactions"""
    assert path.exists(PATH_TO_AMAZON)

    df = pd.read_csv(PATH_TO_AMAZON)
    df.columns = [to_snake(col) for col in df.columns]
    df["original_description"] = df.apply(lambda row: f"{row['title']} : AMZN", axis=1)
    df["original_description"] = df["original_description"].fillna("AMZN: unknown/return")
    df["account_name"] = "AMAZON"
    df["amount"] = df["item_total"].apply(lambda x: float(x.replace("$", "")))
    df["transaction_type"] = "debit"
    df.rename(columns={"order_date": "date"}, inplace=True)

    return df[RAW_TRANSACT_SCHEMA]
