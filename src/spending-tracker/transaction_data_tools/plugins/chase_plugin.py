import re
import pandas as pd
from os import path
from common.constants import *
from datetime import datetime
from app.utils import to_snake
from transaction_data_tools.data_setup_utils import update_raw_transactions_file


CHASE_SCHEMA = [
    "Details",
    "Posting Date",
    "Description",
    "Amount",
    "Type",
    "Balance",
    "Check or Slip #"
]


def get_filename(downloads) -> str:
    """identify chase transaction files"""

    chase_regex = r"chase7973_activity_\d+.csv"

    chase_downloads = []
    for d in downloads:
        match = re.match(chase_regex, d.lower())
        if match:
            chase_downloads.append(match.group())

    dates = []
    for c in chase_downloads:
        date_string = c.replace(".csv", "").split("_")[-1]
        dates.append(datetime.strptime(date_string, '%Y%m%d'))

    if len(dates) > 0:
        max_date = max(dates)
        max_index = dates.index(max_date)

        return chase_downloads[max_index]


def update(downloads) -> str:
    logs = "\n\nUpdating chase records".upper()
    chase_filename = get_filename(downloads)
    if chase_filename:
        logs += update_raw_transactions_file(
            PATH_TO_CHASE, PATH_TO_DOWNLOADS + chase_filename, CHASE_SCHEMA
        )
        return logs
    else:
        return "\n\nNo chase downloads found".upper()


def load_trans() -> pd.DataFrame:
    """Load chase transactions"""
    assert path.exists(PATH_TO_CHASE)

    df = pd.read_csv(PATH_TO_CHASE)
    df.columns = [to_snake(col) for col in df.columns]

    df["date"] = df["posting_date"].apply(lambda x: pd.to_datetime(x).date())
    df["original_description"] = df["description"]
    df["amount"] = df["amount"].apply(abs)
    df["transaction_type"] = df["details"].apply(lambda x: x.lower())
    df["account_name"] = "Chase College"

    return df[RAW_TRANSACT_SCHEMA + ["type"]]

