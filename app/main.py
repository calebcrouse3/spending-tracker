"""
On startup

1. load raw transactions

2. filter out
 transfers
 credit card payments
 robinhood

3. groupby key and get total value

3. load categorized transactions

4. identify uncategorized transactions

5. clear raw transactions

6. assign descriptions from yaml to uncategorized transactions

7. identify any new description -> category maps and update yaml

"""


import pandas as pd
import streamlit as st
import os
import yaml
from SessionState import get_state
from os import path

st.set_page_config(layout="wide", page_title="Spending Tracker")

RAW_TRANSACT_SCHEMA = [
    "date",
    "original_description",
    "description",
    "transaction_type",
    "amount",
    "account_name",
]

CATEGORIZED_TRANSACT_SCHEMA = RAW_TRANSACT_SCHEMA + [
    "category",
    "subcategory",
]

TRANSACT_KEY_COLS = ["date", "original_description", "amount"]


PATH_TO_RAW = "./data/raw/"

PATH_TO_CATEGORIZED = "./data/categorized/"

PATH_TO_DESCRIPTION_MAP = "./app/descriptions.yml"

PATH_TO_CATEGORIES = "./app/categories.yml"


def load_yaml(path):
    with open(path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def to_snake(txt):
    words = txt.lower().split(" ")
    return "_".join(words)


def get_transact_keys(df):
    return df[TRANS_KEY_COLS].drop_duplicates()


def lookup_description(original_description, descr_map):
    # contain to hold any description matches
    # some descriptions might be subsets of other
    matched = []

    # if any phrases in identity_phrases are substring of original_description
    # pretty descript is phrase
    for phrase in descr_map['description_maps']['identity_phrases']:
        if phrase.lower() in original_description.lower():
            matched.append(phrase.title())

    for phrase_map in descr_map['description_maps']['phrase_maps']:
        if phrase_map['key_phrase'].lower() in original_description.lower():
            matched.append(phrase_map['description'].title())

    if len(matched) == 0:
        return original_description
    else:
        lengths = [len(txt) for txt in matched]
        max_len = max(lengths)
        max_len_idx = lengths.index(max_len)
        return matched[max_len_idx]


def get_pretty_descriptions(original_descriptions):
    descr_map = load_yaml(PATH_TO_DESCRIPTION_MAP)
    new_descriptions = []
    for orig in original_descriptions:
        new_descriptions.append(lookup_description(orig, descr_map))
    return new_descriptions


def load_raw_transactions():
    df = pd.read_csv(PATH_TO_RAW + "transactions.csv")
    df.columns = [to_snake(col) for col in df.columns]

    # remove repeated white space characters
    df['original_description'] = df['original_description'].apply(lambda txt: ' '.join(txt.split()))

    # group by all values to aggregate duplicate transactions
    group_df = df.groupby(["date", "original_description", "transaction_type", "account_name"], as_index = False).amount.sum()

    # parse original descriptions to get pretty descriptions
    group_df["description"] = get_pretty_descriptions(group_df["original_description"].values)

    return group_df[RAW_TRANSACT_SCHEMA]


def load_categorized_transactions():
    if path.exists(PATH_TO_CATEGORIZED + "transactions.csv"):
        return pd.load_csv(PATH_TO_CATEGORIZED)
    else:
        return None


def save_categorized_transactions(df):
    batch_paths = [x for x in os.listdir(PATH_TO_CATEGORIZED) if x[-4:] == ".csv"]
    max_batch = (
        -1
        if len(batch_paths) == 0
        else max([int(x.split("_")[1].replace(".csv", "")) for x in batch_paths])
    )
    next_batch_name = f"batch_{str(max_batch+1)}.csv"
    add_header = max_batch == -1
    df.to_csv(PATH_TO_CATEGORIZED + next_batch_name, index=False, header=add_header)


def get_uncategorized_transactions(raw_df, categorized_df):
    """return a batch of uncategorized transactions from raw transactions"""
    if categorized_df == None:
        return raw_df
    else:
        categorized_keys = get_transact_keys(categorized_df)
        categorized_keys.columns = ["cat_" + col for col in categorized_keys.columns]
        join_categorized = raw_df.merge(
            categorized_keys,
            left_on=TRANSACT_KEY_COLS,
            right_on=list(categorized_keys.columns),
            how="left",
        )
        uncategorized_df = join_categorized[join_categorized[categorized_keys.columns[0]].isna()].drop(
            categorized_keys.columns, axis=1
        )
        return uncategorized_df


def categorized_transactions(ss):
    """categorize a batch on new transactions and append them to categorized """
    _navbar()

    # get total number of uncategorized transactions
    n_uncatted = len(ss.uncategorized_transact_df)

    st.title(f"You have {n_uncatted} uncategorized transactions")
    st.title("")

    # TODO space to add new description rules
    new_descript_cols = st.beta_columns((3, 1, 10))
    new_descript_cols[0].text_input("New Description Rule")
    new_descript_cols[1].markdown("")
    new_descript_cols[1].markdown("")
    apply_descript_rule = new_descript_cols[1].button("Apply")
    st.markdown("")

    # if the apply button is hit, add the description and update descriptions in uncategorized
    if apply_descript_rule:
        st.write("applying rule")

    batch_size = 5
    batch_indicies = ss.uncategorized_transact_df.index[0:batch_size]
    uncatted_batch = ss.uncategorized_transact_df.iloc[batch_indicies, :]

    # get total number of columns needed to display data and wigits
    total_ncols = len(uncatted_batch.columns) + 2

    # headers for columns
    header_cols = st.beta_columns(total_ncols)

    for i in range(len(uncatted_batch.columns)):
        header_cols[i].markdown(uncatted_batch.columns[i].upper())

    header_cols[total_ncols - 2].markdown("CATEGORY")
    header_cols[total_ncols - 1].markdown("SUB CATEGORY")

    # container for category_values
    assigned_categories = ["None"] * batch_size
    assigned_subcategories = ["None"] * batch_size

    # write transaction info into grid
    for index, row in uncatted_batch.reset_index(drop=True).iterrows():
        value_cols = st.beta_columns(total_ncols)
        for i in range(len(row.values)):
            value_cols[i].text(row.values[i])

        # suggested_category
        # suggested_subcategory

        selected_category = value_cols[total_ncols - 2].selectbox(
            label="", options=list(ss.categories.keys()), key=f"cat_{index}"
        )
        assigned_categories[index] = selected_category

        selected_subcategory = value_cols[total_ncols - 1].selectbox(
            label="",
            options=ss.categories[assigned_categories[index]],
            key=f"subcat_{index}",
        )
        assigned_subcategories[index] = selected_subcategory

        st.markdown("---")

    submit = st.button("Submit and Proceed")

    if submit:
        uncatted_batch["category"] = assigned_categories
        uncatted_batch["subcategory"] = assigned_subcategories
        save_categorized_transactions(uncatted_batch)


def display_trends(ss):
    _navbar()
    st.write(ss.categorized_transact_df)
    st.write("This is where the trends will go")


def load_categories():
    cats_yaml = load_yaml(PATH_TO_CATEGORIES)
    categories = {}
    for cat in cats_yaml['categories']:
        categories[cat["name"]] = cat["subcategories"]
    return categories


def home_page():
    _navbar()
    st.write("Welcome to your spending tracker!")


def _navbar() -> None:
    """Display navbar."""
    cols = st.beta_columns(8)

    cols[0].markdown(
        f"<a href='/'>&#128200; Home</a>",
        unsafe_allow_html=True,
    )

    cols[1].markdown(
        f"<a href='/?page=categorize'>&#128269; Categorize</a>",
        unsafe_allow_html=True,
    )

    cols[2].markdown(
        f"<a href='/?page=trends'>&#128200; Trends</a>",
        unsafe_allow_html=True,
    )

    st.markdown("---")


def _main() -> None:

    # create session state
    ss = get_state()

    # it session state not initialized, intialize data frames in session state
    if ss.initialized == None:
        ss.raw_transact_df = load_raw_transactions()
        ss.categorized_transact_df = load_categorized_transactions()
        ss.uncategorized_transact_df = get_uncategorized_transactions(
            ss.raw_transact_df,
            ss.categorized_transact_df,
        )
        ss.initialized = True
        # raw transactions not needed to clear from state
        ss.categories = load_categories()
        ss.raw_transact_df = None
        # TODO
        # ss.description_category_map = get_description_category_map()

    params = st.experimental_get_query_params()
    page = params.get("page", ["home"])[0]

    if page == "home":
        home_page()

    elif page == "categorize":
        categorized_transactions(ss)

    elif page == "trends":
        display_trends(ss)

    else:
        _navbar()
        st.write("not a page")

    ss.sync()


if __name__ == "__main__":
    _main()
