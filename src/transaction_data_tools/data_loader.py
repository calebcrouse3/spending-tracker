import os
import pandas as pd
import datetime
from datetime import date
from app.utils import to_snake
from common.constants import *
from transaction_data_tools.plugins.amazon_plugin import load_trans as _load_amazon_trans


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

    return group_df[RAW_TRANSACT_SCHEMA]


def load_raw_trans() -> pd.DataFrame:
    """Load all raw transactions and combine them"""
    mint_df = load_mint_trans()
    amzn_df = _load_amazon_trans()

    # union together
    raw_trans = pd.concat([mint_df, amzn_df])

    # get transaction in descending order
    raw_trans["date"] = raw_trans["date"].apply(lambda x: pd.to_datetime(x).date())
    min_trans_date = datetime.date(MIN_YEAR, MIN_MONTH, MIN_DAY)
    filtered_trans = raw_trans[raw_trans["date"] >= min_trans_date]
    filtered_trans.sort_values("date", ascending=False, inplace=True)

    # filtered_trans.reset_index(inplace=True, drop=True)
    filtered_trans.drop_duplicates(inplace=True)

    return filtered_trans


def load_catted_trans(catted_exists):
    """Load categorized transactions"""
    if catted_exists:
        df = pd.read_csv(PATH_TO_CATEGORIZED_TRANSACT)
        # cast date to datetime so it can join to date for raw trans in order to get uncatted trans
        df["date"] = df["date"].apply(lambda x: pd.to_datetime(x).date())
        return df