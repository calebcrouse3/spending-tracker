import os
import pandas as pd
from common.constants import *


def load_mint_transact() -> pd.DataFrame:
    # check that there is only one file in mint folder
    mint_files = os.listdir(PATH_TO_MINT_FOLDER)

    if len(mint_files) == 1:
        df = pd.read_csv(PATH_TO_MINT_FOLDER + mint_files[0])
        df.columns = [to_snake(col) for col in df.columns]

        # remove repeated white space characters
        df['original_description'] = df['original_description'].apply(lambda txt: ' '.join(txt.split()))

        # group by all values to aggregate duplicate transactions
        group_df = df.groupby([
            "date",
            "original_description",
            "transaction_type",
            "account_name"],
            as_index=False
        ).amount.sum()

        group_df["amount"] = group_df["amount"].round(2)

        return group_df[RAW_TRANSACT_SCHEMA]

    else:
        print("Mint folder needs attention!")


def load_amazon_transact() -> pd.DataFrame:
    # check that there is only one file in mint folder
    amzn_files = os.listdir(PATH_TO_AMAZON_FOLDER)

    if len(amzn_files) == 1:
        df = pd.read_csv(PATH_TO_AMAZON_FOLDER + amzn_files[0])
        df.columns = [to_snake(col) for col in df.columns]
        df["original_description"] = ("AMZN: " + df["title"] + " " + df["category"]).fillna("AMZN: unknown item / return")
        df["account_name"] = "AMAZON"
        df["amount"] = df["item_total"].apply(lambda x: float(x.replace("$", "")))
        df["transaction_type"] = "debit"
        df.rename(columns={"order_date": "date"}, inplace=True)

        return df[RAW_TRANSACT_SCHEMA]

    else:
        print("Amazon folder needs attention!")
        return None


def load_raw_trans() -> pd.DataFrame:
    # load individual sources of raw transactions
    mint_df = load_mint_transact()
    amzn_df = load_amazon_transact()

    # union together
    raw_trans = pd.concat([mint_df, amzn_df])

    # get transaction in descending order
    raw_trans["date"] = raw_trans["date"].apply(lambda x: pd.to_datetime(x))
    raw_trans.sort_values("date", ascending = False, inplace = True)
    raw_trans["date"] = raw_trans["date"].dt.strftime('%m/%d/%Y')
    raw_trans.reset_index(inplace = True, drop = True)

    return raw_trans


def load_catted_transact():
    if ss.catted_exists:
        return pd.read_csv(PATH_TO_CATEGORIZED_TRANSACT + MASTER_TRANSACT_FILE_NAMES)
    return None


def save_categorized_transactions():
    batch_paths = [x for x in os.listdir(PATH_TO_CATEGORIZED) if x[-4:] == ".csv"]
    max_batch = (
        -1
        if len(batch_paths) == 0
        else max([int(x.split("_")[1].replace(".csv", "")) for x in batch_paths])
    )
    next_batch_name = f"batch_{str(max_batch+1)}.csv"
    add_header = max_batch == -1
    df.to_csv(PATH_TO_CATEGORIZED + next_batch_name, index=False, header=add_header)
