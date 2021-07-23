import re
import os
import shutil
import time
import pandas as pd
from common.constants import *
from data_setup.amazon_plugin import get_amazon_filenames, AMAZON_SCHEMA
from data_setup.mint_plugin import get_latest_mint_filename, MINT_SCHEMA


def _update_raw_transactions_file(transact_file_path, new_file_path, subcols) -> str:
    """takes the current csv in folder and new appends data from files in downloads"""

    logs = f"\n\nupdating: {transact_file_path}"
    logs += f"\n\nusing: {new_file_path}"

    new_df = pd.read_csv(new_file_path)[subcols]
    new_df.drop_duplicates(inplace=True)

    # if previous raw transactions exist
    if os.path.exists(transact_file_path):

        curr_df = pd.read_csv(transact_file_path)[subcols]
        concat_dfs = pd.concat([curr_df, new_df])[subcols]
        concat_dfs.drop_duplicates(inplace=True)

        logs += f"\n\nNew transactions: {len(concat_dfs) - len(curr_df)}. Total: {len(concat_dfs)}"

        # overwrite with updated transactions
        concat_dfs.to_csv(transact_file_path, index=False)

    else:
        # save new file as raw transactions
        new_df.to_csv(transact_file_path, index=False)
        logs += f"\n\nNo existing transactions. Total: {len(new_df)}"

    return logs + "\n\n" + "-" * 20


def update() -> str:
    downloads = os.listdir(PATH_TO_DOWNLOADS)

    logs = "\n\nUpdating mint records".upper()

    # get the filename of the most recent mint download
    mint_filename = get_latest_mint_filename(downloads)
    logs += _update_raw_transactions_file(PATH_TO_MINT, PATH_TO_DOWNLOADS + mint_filename, MINT_SCHEMA)

    logs += "\n\nUpdating amazon records".upper()

    # get all the filenames of amazon order reports
    amazon_filenames = get_amazon_filenames(downloads)
    for file in amazon_filenames:
        logs += _update_raw_transactions_file(PATH_TO_AMAZON, PATH_TO_DOWNLOADS + file, AMAZON_SCHEMA)

    return logs
