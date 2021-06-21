import re

class describer():
    def __init__(self):
        self.description_map = self.get_description_map()
        self.regex_filters = self.get_regex_filters()


    def get_pretty_description(self, descr):

        # first check if keyword exists for description map
        for key, value in self.description_map.items():
            if  key.lower() in descr.lower():
                return value

        # if not just apply the regex filter and
        return self.regex_filter(descr)


    def regex_filter(self, descr):
        new_descr = descr
        for pattern in self.regex_filters:
            new_descr = re.sub(pattern, '', new_descr)
        return new_descr


    def get_description_map(self):
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
            'northside':' Northside Social'
        }
        return DESCRIPTION_MAP

    def get_regex_filters(self):
        REGEX_FILTERS = [
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
        return REGEX_FILTERS
