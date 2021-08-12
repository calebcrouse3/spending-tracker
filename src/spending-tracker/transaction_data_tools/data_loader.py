import os
import pandas as pd
import datetime
from datetime import date
from app.utils import to_snake
from common.constants import *
from transaction_data_tools.plugins.amazon_plugin import load_trans as _load_amazon_trans
from transaction_data_tools.plugins.mint_plugin import load_trans as _load_mint_trans


def load_raw_trans() -> pd.DataFrame:
    """Load all raw transactions and combine them"""
    mint_df = _load_mint_trans()
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
