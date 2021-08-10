from os import path
import pandas as pd


def update_raw_transactions_file(transact_file_path, new_file_path, subcols) -> str:
    """takes the current csv in folder and new appends transaction_data from files in downloads"""

    logs = f"\n\nupdating: {transact_file_path}"
    logs += f"\n\nusing: {new_file_path}"

    new_df = pd.read_csv(new_file_path)[subcols]
    new_df.drop_duplicates(inplace=True)

    # if previous raw transactions exist
    if path.exists(transact_file_path):

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
