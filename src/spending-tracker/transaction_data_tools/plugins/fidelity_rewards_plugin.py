import re
import pandas as pd
from common.constants import *
from datetime import datetime
from transaction_data_tools.data_setup_utils import update_raw_transactions_file


FIDELITY_REWARDS_SCHEMA = [
    "Date",
    "Transaction",
    "Name",
    "Memo",
    "Amount"
]


def get_filenames(downloads) -> str:
    """identify all fidelity_credit_card transactions"""

    regex = r"fidelity.*credit.*\.csv"

    files = []
    for d in downloads:
        match = re.match(regex, d)
        if match:
            files.append(match.group())

    return files


def update(downloads) -> str:
    logs = "\n\nUpdating fidelity credit card records".upper()
    filenames = get_filenames(downloads)
    for file in filenames:
        logs += update_raw_transactions_file(
            PATH_TO_FIDELITY_REWARDS, PATH_TO_DOWNLOADS + file, FIDELITY_REWARDS_SCHEMA
        )
    return logs


def load_trans() -> pd.DataFrame:
    """Load fidelity rewards transactions"""
    assert path.exists(PATH_TO_FIDELITY_REWARDS)

    df = pd.read_csv(PATH_TO_FIDELITY_REWARDS)
    df.columns = [to_snake(col) for col in df.columns]

    df["original_description"] = df["name"]
    df["date"] = df["date"].apply(lambda x: pd.to_datetime(x).date())
    df["transaction_type"] = df["transaction"].apply(lambda x: x.lower())
    df["amount"] = df["amount"].apply(abs)
    df["account_name"] = "Fidelity Rewards"

    return df[RAW_TRANSACT_SCHEMA]