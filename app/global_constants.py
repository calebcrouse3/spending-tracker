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

MASTER_TRANSACT_FILE_NAMES = "transactions.csv"

DOWNLOADS_FOLDER = "/Users/caleb.crouse/Downloads"

TRANSACT_KEY_COLS = ["date", "original_description", "amount"]

PATH_TO_MINT_FOLDER = "./data/raw/mint/"

PATH_TO_AMAZON_FOLDER = "./data/raw/amazon/"

PATH_TO_CATEGORIZED = "./data/categorized/" + MASTER_TRANSACT_FILE_NAMES

PATH_TO_DESCRIPTION_MAP = "./app/descriptions.yml"

PATH_TO_CATS = "./app/categories.yml"
