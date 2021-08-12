RAW_TRANSACT_SCHEMA = [
    "date",
    "transaction_type",
    "amount",
    "account_name",
    "original_description",
]

CATEGORIZED_TRANSACT_SCHEMA = RAW_TRANSACT_SCHEMA + [
    "description",
    "category",
    "subcategory",
]

TRANSACT_KEY_COLS = ["date", "original_description"]

MASTER_TRANSACT_FILE_NAMES = "transactions.csv"

PATH_TO_DESCRIPTION_CONF = "/src/common/descriptions.yml"

PATH_TO_CATEGORIES_CONF = "/src/common/categories.yml"

PATH_TO_MINT = "/src/transaction_data/raw/mint/" + MASTER_TRANSACT_FILE_NAMES

PATH_TO_CHASE = "/src/transaction_data/raw/chase/" + MASTER_TRANSACT_FILE_NAMES

PATH_TO_AMAZON = "/src/transaction_data/raw/amazon/" + MASTER_TRANSACT_FILE_NAMES

PATH_TO_FIDELITY_REWARDS = "/src/transaction_data/raw/fidelity_rewards/" + MASTER_TRANSACT_FILE_NAMES

PATH_TO_FIDELITY_CASH = "/src/transaction_data/raw/fidelity_cash/" + MASTER_TRANSACT_FILE_NAMES

PATH_TO_CATEGORIZED_TRANSACT = "/src/transaction_data/categorized/" + MASTER_TRANSACT_FILE_NAMES

PATH_TO_DOWNLOADS = "/src/transaction_data/downloads/"

MIN_YEAR = 2020
MIN_MONTH = 6
MIN_DAY = 1
