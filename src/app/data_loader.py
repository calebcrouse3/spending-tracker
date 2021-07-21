import os
import pandas as pd
from app.utils import to_snake
from common.constants import *


def load_mint_trans() -> pd.DataFrame:
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

    # remove amzn transactions
    def is_amazon_trans(descr) -> bool:
        substrings = ["amzn", "amazon"]
        for s in substrings:
            if s in descr.lower():
                return True
        return False

    group_df = group_df[~group_df["original_description"].apply(is_amazon_trans)]
    group_df["amount"] = group_df["amount"].round(2)

    return group_df[RAW_TRANSACT_SCHEMA]


def load_amazon_trans() -> pd.DataFrame:
    """Load raw amazon transactions"""
    assert os.path.exists(PATH_TO_AMAZON)

    df = pd.read_csv(PATH_TO_AMAZON)
    df.columns = [to_snake(col) for col in df.columns]
    df["original_description"] = df.apply(lambda row: row['title'], axis=1)
    df["original_description"] = df["original_description"].fillna("AMZN: unknown/return")
    df["account_name"] = "AMAZON"
    df["amount"] = df["item_total"].apply(lambda x: float(x.replace("$", "")))
    df["transaction_type"] = "debit"
    df.rename(columns={"order_date": "date"}, inplace=True)

    return df[RAW_TRANSACT_SCHEMA]


def load_raw_trans() -> pd.DataFrame:
    """Loadd all raw transactions and combine them"""
    mint_df = load_mint_trans()
    amzn_df = load_amazon_trans()

    # union together
    raw_trans = pd.concat([mint_df, amzn_df])

    # get transaction in descending order
    raw_trans["date"] = raw_trans["date"].apply(lambda x: pd.to_datetime(x))
    raw_trans.sort_values("date", ascending=False, inplace=True)

    # after sorting, convert date back to readable form
    raw_trans["date"] = raw_trans["date"].dt.strftime('%m/%d/%Y')
    raw_trans.reset_index(inplace=True, drop=True)
    raw_trans.drop_duplicates(inplace=True)

    return raw_trans


def load_catted_trans(catted_exists):
    """Load categorized transactions"""
    if catted_exists:
        return pd.read_csv(PATH_TO_CATEGORIZED_TRANSACT)
