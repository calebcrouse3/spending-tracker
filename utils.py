import re
import os
from os import path
import shutil
from app.global_constants import *
import time
import pandas as pd

# using this subset of columns corrected with deduplication errors
AMAZON_COLS = [
    "Order Date",
    "Order ID",
    "Title",
    "Category",
    "Seller",
    "Item Total"
]

MINT_COLS = [
    "Date",
    "Description",
    "Original Description",
    "Amount",
    "Transaction Type",
    "Category",
    "Account Name",
]


def append_new_transactions(transact_file_path, new_file_path, subcols):
    """takes the current csv in folder and appends data from new file"""



    print("")
    print(f"updating: {transact_file_path}")
    print(f"using: {new_file_path}")

    new_df = pd.read_csv(new_file_path)[subcols]
    new_df.drop_duplicates(inplace = True)

    # if transaction file exists
    if path.exists(transact_file_path):

        curr_df = pd.read_csv(transact_file_path)[subcols]
        curr_df.drop_duplicates(inplace = True)

        concat_dfs = pd.concat([curr_df, new_df])[subcols]
        concat_dfs.drop_duplicates(inplace = True)

        print(f"new records {len(concat_dfs) - len(curr_df)}: total records {len(concat_dfs)}")

        # overwrite with updated df's
        concat_dfs.to_csv(transact_file_path, index = False)

    # if it doesnt exist
    else:
        # save new file as transactions
        new_df.to_csv(transact_file_path, index = False)
        print(f"no existing records. new records {len(new_df)}")




def update_raw_transactions():
    downloads = os.listdir(DOWNLOADS_FOLDER)

    print("\nupdating mint records".upper())

    # get the filename of the most recent mint download
    mint_file_name = get_last_mint(downloads)
    append_new_transactions(PATH_TO_MINT_FOLDER + MASTER_TRANSACT_FILE_NAMES, DOWNLOADS_FOLDER + "/" + mint_file_name, MINT_COLS)

    print("\nupdating amazon records".upper())

    # get all the filenames of amazon order reports
    amzn_file_names = get_all_amzn(downloads)
    for amzn_file_name in amzn_file_names:
        time.sleep(3)
        append_new_transactions(PATH_TO_AMAZON_FOLDER + MASTER_TRANSACT_FILE_NAMES, DOWNLOADS_FOLDER + "/" + amzn_file_name, AMAZON_COLS)


def get_all_amzn(downloads):
    """identify all amzn order histories"""
    amzn_regex = r"\d{2}-\w{3}-\d{4}_to_\d{2}-\w{3}-\d{4}(\s\((\d+)\))?\.csv"

    amzn_downloads = []
    for d in downloads:
        match = re.match(amzn_regex, d)
        if match:
            amzn_downloads.append(match.group())

    return amzn_downloads


def get_last_mint(downloads):
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
        max_ind = max([x for x in mint_downloads if x != None])
        return f"transactions ({max_ind}).csv"


update_raw_transactions()
