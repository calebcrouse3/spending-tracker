RAW_TRANSACT_SCHEMA = [
    "date",
    "original_description",
    "transaction_type",
    "amount",
    "account_name",
]

CATEGORIZED_TRANSACT_SCHEMA = RAW_TRANSACT_SCHEMA + [
    "description",
    "category",
    "subcategory",
]

TRANSACT_KEY_COLS = ["date", "original_description", "amount"]

MASTER_TRANSACT_FILE_NAMES = "transactions.csv"

PATH_TO_DESCRIPTION_CONF = "/src/common/descriptions.yml"

PATH_TO_CATEGORIES_CONF = "/src/common/categories.yml"

PATH_TO_MINT = "/src/data/raw/mint/" + MASTER_TRANSACT_FILE_NAMES

PATH_TO_AMAZON = "/src/data/raw/amazon/" + MASTER_TRANSACT_FILE_NAMES

PATH_TO_CATEGORIZED_TRANSACT = "/src/data/categorized/" + MASTER_TRANSACT_FILE_NAMES

PATH_TO_DOWNLOADS = "/src/data/downloads/"

MIN_YEAR = 2020
MIN_MONTH = 6
MIN_DAY = 1

