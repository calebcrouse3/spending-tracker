My spending tracker

Abbreviation Guide:
- trans: transaction(s)
- (sub)cat(s): (sub)category(s)
- descr: description(s)
- (un)catted: (un)categorized

data:
raw data holds transaction in mostly original from from data source. They keep
a ledger of all the unique transactions from that data source. These file are updated
during initialization. Categorized holds transactions that have been given a Category
and follow the transaction schema.

data_setup:
Looks in the downloads folder and uses the plugins to identify new files from
the plugin data source (mint, amazon). It then updates the raw data in the respective
raw data folders

plugins:
Define how to look for the file name from the respective file sources and the
schemas to expect from those data sources

load_raw_data:
loads and concats all the raw data, maps them to the transaction schema, groups amounts
by date and transcription (fixes duplicate purchases at same venue on the same date, think drinks at the bar)
and assigns this to raw transactions.

descriptions:
Two types.
Identity description: If "identity_phrases" in original_desc, pretty descr = "identity_phrases"
Phrase map description: If "key_phrase" in original_desc, pretty descr = "description"

initialize:
Sets up all the initial data, only run once on start, is when the uncategorized transactions
are identified by finding the difference between raw data and categorized transactions

categorizing transactions:
sorted uncategorized transaction by time reverse order. Iterate over batches of transactions.
For each batch, get the pretty description, get the suggested categories and subcategories,
take the data from the drop downs and fill in those as columns in the batch, on submit,
save the batch to the categorized transactions both in memory and on disk, then update the
description to category map so next batches can use those suggestions.

category suggestions:
Is a map of pretty descriptions to categories and subcategories that is generated
from the categorized data where the most popular categories for each pretty description is used

TODO:
- Check what happens when filtered_trans == 0. IE no more transactions to categorize or time selection after today
