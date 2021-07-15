import re

AMAZON_SCHEMA = [
    "Order Date",
    "Order ID",
    "Title",
    "Category",
    "Seller",
    "Item Total"
]


def get_amazon_filenames(downloads):
    """identify all amzn order histories"""
    amzn_regex = r"\d{2}-\w{3}-\d{4}_to_\d{2}-\w{3}-\d{4}(\s\((\d+)\))?\.csv"

    amzn_downloads = []
    for d in downloads:
        match = re.match(amzn_regex, d)
        if match:
            amzn_downloads.append(match.group())

    return amzn_downloads
