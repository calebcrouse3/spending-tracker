# map for credit descriptions. If description contains key, change description to value
DESCRIPTION_MAP = {
    'ironnet': 'Ironnet Cybersecuirty',
    'robinhood': 'Robinhood',
    'home depot': 'Home Depot',
    'amzn': 'Amazon',
    'amazon': 'Amazon',
    'venmo': 'Venmo',
    'cromwell': 'crowmell zelle',
    'zelle': 'zelle',
    'remote online deposit': 'remote online deposit',
    'simple': 'Simple Bank',
    'atm': 'ATM',
    'education student ln': 'student loans',
    'coinbase': 'Coinbase',
    'chase card': 'chase card',
    'citi': 'Citi Card',
    'usaa': 'USAA',
    'VHC': 'VHC',
    'harris': 'Harris Teeter',
    'parking': 'parking fee',
    'garag': 'parking fee',
    'parkmobile': 'parking fee',
    'long term': 'parking fee',
    '5guys': '5 Guys',
    'prime video': 'prime video',
    'cubesmart': 'CubeSmart',
    'hbo': 'HBO',
    'bird app': 'Bird',
    'bund up': 'Bund Up',
    'total wine': 'Total Wine',
    'bread & water': 'Bread & Water',
    'foreign exchange rate adjustment fee': 'foreign exchange fee',
    'giant': 'Giant Groceries',
    'idego': 'Idego',
    'goat': 'GOAT',
    'lim*ride': 'lim*ride',
    'onlyfans': 'onlyfans',
    'postmates': 'postmates',
    'philz coffee': 'philz coffee',
}

# list of regex matches to filter out of descriptions
DESCRIPTION_REGEX_FILTERS = [
    # only digits word
    '\s\d+',

    # state and forward slash
    '\s[A-Z]{1,2}/[0-9]{2}',

    # filter LLC extension
    ', LLC.*',
    'LLC.*',

    # filter website extension
    '\sWWW.*',
    '\s\S\.com',

    # simple filters
    '\sWEB\s',
    'ID:',

    'TST\*\s',

    '\sHTTP.*',
]

def get_config():
    config = {}
    config["DESCRIPTION_MAP"] = DESCRIPTION_MAP
    config["DESCRIPTION_REGEX_FILTERS"] = DESCRIPTION_REGEX_FILTERS
    return config
