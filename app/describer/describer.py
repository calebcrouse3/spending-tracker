import re
import pandas
from desciber_config import get_config


class describer():
    def __init__(self, prev_desc):
        self.prev_desc = prev_desc
        self.config = get_config()


    def get_pretty_description(self, descr):

        # first check if keyword exists for description map
        for key, value in self.config["DESCRIPTION_MAP"].items():
            if  key.lower() in descr.lower():
                return value

        # if not just apply the regex filter and
        return regex_filter(descr)


    def regex_filter(descr):
        new_descr = descr
        for pattern in self.config["DESCRIPTION_REGEX_FILTERS"]:
            new_descr = re.sub(pattern, '', new_descr)
        return new_descr
