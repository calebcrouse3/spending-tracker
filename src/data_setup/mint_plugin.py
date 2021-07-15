import re

MINT_SCHEMA = [
    "Date",
    "Description",
    "Original Description",
    "Amount",
    "Transaction Type",
    "Category",
    "Account Name",
]


def get_latest_mint_filename(downloads):
    """identify filename of most recent mint download"""
    mint_regex = r"transactions(\s\((\d+)\))?\.csv"

    # get all mint downloads
    mint_downloads = []
    for d in downloads:
        match = re.match(mint_regex, d)
        if match:
            if match.group(2):
                mint_downloads.append(int(match.group(2)))

    if len(mint_downloads) == 0:
        return "transactions.csv"
    elif len(mint_downloads) > 0:
        max_ind = max([x for x in mint_downloads if x])
        return f"transactions ({max_ind}).csv"
