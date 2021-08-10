from os import listdir
from common.constants import *
from transaction_data_tools.plugins.amazon_plugin import update as _update_amazon
from transaction_data_tools.plugins.chase_plugin import update as _update_chase


def update() -> str:
    downloads = listdir(PATH_TO_DOWNLOADS)
    amazon_logs = _update_amazon(downloads)
    chase_logs = _update_chase(downloads)
    return amazon_logs + chase_logs
