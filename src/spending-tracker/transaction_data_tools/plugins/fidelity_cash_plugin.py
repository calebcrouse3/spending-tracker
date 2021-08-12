import re
import pandas as pd
from common.constants import *
from datetime import datetime
from transaction_data_tools.data_setup_utils import update_raw_transactions_file


FIDELITY_CASH_SCHEMA = []


def get_filenames(downloads) -> str:
    """identify all fidelity_credit_card transactions"""

    regex = r"History_for_Account_Z07707961.*\.csv"

    files = []
    for d in downloads:
        match = re.match(regex, d)
        if match:
            files.append(match.group())

    return files


def update(downloads) -> str:
    logs = "\n\nUpdating fidelity cash records".upper()
    filenames = get_filenames(downloads)
    for file in filenames:
        logs += update_raw_transactions_file(
            PATH_TO_FIDELITY_CASH, PATH_TO_DOWNLOADS + file, FIDELITY_CASH_SCHEMA
        )
    return logs


def load_trans() -> pd.DataFrame:
    pass