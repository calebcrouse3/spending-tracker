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

PATH_TO_DESCRIPTION_MAP = "./app/descriptions.yml"

PATH_TO_CATS = "./app/categories.yml"
