"""Streamlit spending tracker app."""
import os
import yaml
import pandas as pd
import streamlit as st
import datetime
from SessionState import get_state
from data_setup.raw_data import update as _update_raw_data
from data_loader import load_raw_trans, load_catted_trans
from app.utils import to_snake, load_yaml, save_yaml, sort_cats
from category_manager import manager_page
from common.constants import *

st.set_page_config(layout="wide", page_title="Spending Tracker")

ss = get_state()


def lookup_description(original_description):
    """get the pretty description for an original description string"""

    # container to hold any description matches
    # some descriptions might be subsets of other
    matched = []

    # if any phrases in identity_phrases are substring of original_description
    # add identity phrase to matched
    for phrase in ss.descr['identity_phrases']:
        if phrase.lower() in original_description.lower():
            matched.append(phrase.title())

    # if any key_phrases in phrase_maps are substring of original_description
    # add description associated with key_phrase to matched
    for phrase_map in ss.descr['phrase_maps']:
        if phrase_map['key_phrase'].lower() in original_description.lower():
            matched.append(phrase_map['description'].title())

    if len(matched) == 0:
        return original_description
    else:
        # return the longest matched description because its probably the most specific
        lengths = [len(txt) for txt in matched]
        max_len = max(lengths)
        max_len_idx = lengths.index(max_len)
        return matched[max_len_idx]


def get_transact_keys(df):
    """get a df with unique transaction keys"""
    return df[TRANSACT_KEY_COLS].drop_duplicates()


def get_uncatted_trans():
    """return set of raw transactions which have not already been categorized"""
    if not ss.catted_exists:
        return ss.raw_trans_df.copy().reset_index(drop=True)
    else:
        categorized_keys = get_transact_keys(ss.catted_trans_df)
        categorized_keys.columns = ["cat_" + col for col in categorized_keys.columns]

        join_categorized = ss.raw_trans_df.merge(
            categorized_keys,
            left_on=TRANSACT_KEY_COLS,
            right_on=list(categorized_keys.columns),
            how="left",
        )

        uncategorized_df = join_categorized[join_categorized[categorized_keys.columns[0]].isna()].drop(
            categorized_keys.columns, axis=1
        )
        return uncategorized_df[RAW_TRANSACT_SCHEMA].reset_index(drop=True)


def lookup_category(descr):
    """gets the index of the correct category/subcategory in ss.cats"""
    if descr in ss.descr_cat_map.keys():
        category = ss.descr_cat_map[descr]["category"]
        subcategory = ss.descr_cat_map[descr]["subcategory"]
        # find index of category in ss.cats
        cat_list = list(ss.cats.keys())
        cat_index = cat_list.index(category)
        subcat_list = ss.cats[category]
        subcat_index = subcat_list.index(subcategory)
        return cat_index, subcat_index
    else:
        return 0, 0


def update_descr_conf(rule_txt, rule_type):
    """adds a new description to ss and overwrites yamls"""

    if rule_type == "identity":
        ss.descr["identity_phrases"] += [rule_txt]

    elif rule_type == "phrase_map":
        new_phrase = {}

        split_kv = rule_txt.split(":")
        new_phrase["key_phrase"] = split_kv[0].replace("'", "").strip()
        new_phrase["description"] = split_kv[1].replace("'", "").strip()

        ss.descr["phrase_maps"] += [new_phrase]

    # overwrite yaml file with updated state
    save_yaml(PATH_TO_DESCRIPTION_CONF, ss.descr)


def categorized_trans():
    """categorize a batch of new transactions and append them to categorized"""
    _navbar()

    # columns for title and wigits
    wigit_cols = st.beta_columns((10, 3, 3, 3))

    # description rule adder wigit
    descr_rule_def = wigit_cols[1].text_input("New Description Rule")
    wigit_cols[2].markdown("")
    wigit_cols[2].markdown("")
    apply_descript_rule = wigit_cols[2].button("Apply")

    # if desription apply button clicked
    if apply_descript_rule:
        rule_type = "phrase_map" if ":" in descr_rule_def else "identity"
        update_descr_conf(descr_rule_def, rule_type)

    # get total number of uncategorized transactions
    n_uncatted = len(ss.uncatted_trans_df)

    wigit_cols[0].title(f"You have {n_uncatted} uncategorized transactions")
    st.title("")

    # pluck off top n rows of uncatted trans
    desired_batch_size = 5
    batch_size = desired_batch_size if desired_batch_size < n_uncatted else n_uncatted
    batch_indicies = ss.uncatted_trans_df.index[0:batch_size]
    uncatted_batch = ss.uncatted_trans_df.loc[batch_indicies, :]

    # add pretty descriptions
    uncatted_batch["description"] = uncatted_batch["original_description"].apply(lambda x: lookup_description(x))

    # get total number of columns needed to display data and category selectors
    total_ncols = len(uncatted_batch.columns) + 2
    cols_spacing = total_ncols

    # headers for columns
    header_cols = st.beta_columns(cols_spacing)

    # write column headers
    for i in range(len(uncatted_batch.columns)):
        header_cols[i].markdown(uncatted_batch.columns[i].upper())

    header_cols[total_ncols - 2].markdown("CATEGORY")
    header_cols[total_ncols - 1].markdown("SUB CATEGORY")

    # container for selected category values
    assigned_cats = ["None"] * batch_size
    assigned_subcats = ["None"] * batch_size

    # write transaction info into grid
    for index, row in uncatted_batch.reset_index(drop=True).iterrows():
        value_cols = st.beta_columns(cols_spacing)
        for i in range(len(row.values)):
            value_cols[i].text(row.values[i])

        # get index in cats dictionary of suggested categoies based on this description
        sugg_cat, sugg_subcat = lookup_category(row["description"])

        # create select box for category
        selected_category = value_cols[total_ncols - 2].selectbox(
            label="",
            options=list(ss.cats.keys()),
            key=f"cat_{index}",
            index=sugg_cat,
        )
        assigned_cats[index] = selected_category

        # create select box for subcategory with values based on selected category
        selected_subcategory = value_cols[total_ncols - 1].selectbox(
            label="",
            options=ss.cats[assigned_cats[index]],
            key=f"subcat_{index}",
            index=sugg_subcat,
        )
        assigned_subcats[index] = selected_subcategory

        st.markdown("---")

    submit = st.button("Submit and Proceed")

    if submit:
        # add category and subcategory assignments to batch
        uncatted_batch["category"] = assigned_cats
        uncatted_batch["subcategory"] = assigned_subcats

        # append batch to categorized transactions
        if ss.catted_exists:
            ss.catted_trans_df = pd.concat([
                ss.catted_trans_df,
                uncatted_batch[CATEGORIZED_TRANSACT_SCHEMA]
            ])
        else:
            ss.catted_trans_df = uncatted_batch[CATEGORIZED_TRANSACT_SCHEMA]
            ss.catted_exists = True

        # remove categorized transactions from uncategorized transaction in memory
        ss.uncatted_trans_df.drop(batch_indicies, inplace=True)

        # overwrite file with saved transactions to persist categorizations to disk
        ss.catted_trans_df.to_csv(PATH_TO_CATEGORIZED_TRANSACT, index=False)

        # update description category map with new categorized transactions
        # ensures that same descriptions in next batches will get cat and subcat suggestions
        ss.descr_cat_map = get_descr_cat_map()


def display_trends():
    _navbar()
    st.text("cats")
    st.write(ss.cats)
    st.text("descr")
    st.write(ss.descr)
    st.text("descr_cats_map")
    st.write(ss.descr_cat_map)
    st.text("catted_exists")
    st.write(ss.catted_exists)


def home_page():
    _navbar()
    st.write("Welcome to your spending tracker!")


def get_descr_cat_map():
    """gets a mapping from pretty descriptions to most common category
    using previously categorized transactions"""

    descr_cat_map = {}

    if ss.catted_exists:
        # get count of category/subcategory per description
        cat_count = ss.catted_trans_df.groupby(
            ["description", "category", "subcategory"],
            as_index=False
        ).date.count().rename(columns={"date": "count"})

        # sort by cat count desc, description asc for pseduo partition in next step
        cat_count.sort_values(["description", "count"], ascending=[True, False], inplace=True)

        # row order partitioned by description
        cat_count["row_num"] = cat_count.groupby("description").cumcount() + 1

        # first row
        first_row_df = cat_count.loc[cat_count["row_num"] == 1, ["description", "category", "subcategory"]]

        for index, row in first_row_df.iterrows():
            descr_cat_map[row["description"]] = {
                "category": row["category"],
                "subcategory": row["subcategory"]
                }

    return descr_cat_map


def text_and_button(label):
    cols = st.beta_columns(10)
    txt = cols[0].text_input(label)
    cols[1].markdown("")
    cols[1].markdown("")
    apply_it = cols[1].button("Apply")
    return txt, apply_it


def initialize() -> None:
    sort_cats()
    ss.update_logs = _update_raw_data()
    ss.page = "home"
    ss.initialized = True
    ss.raw_trans_df = load_raw_trans()
    ss.catted_exists = os.path.exists(PATH_TO_CATEGORIZED_TRANSACT)
    ss.catted_trans_df = load_catted_trans(ss.catted_exists)
    ss.uncatted_trans_df = get_uncatted_trans()
    ss.cats = load_yaml(PATH_TO_CATEGORIES_CONF)
    ss.descr = load_yaml(PATH_TO_DESCRIPTION_CONF)
    ss.descr_cat_map = get_descr_cat_map()
    ss.raw_trans_df = None


def _navbar() -> None:
    """Display navbar."""
    cols = st.beta_columns(10)

    home_button = cols[0].button("Home")
    catz_button = cols[1].button("Categorize")
    trends_button = cols[2].button("Trends")
    manager_button = cols[3].button("Manager")
    debug = cols[9].checkbox("debug-mode")

    if debug:
        cat_df = cols[4].button("df-categorized")
        uncat_df = cols[5].button("df-uncategorized")
        update_logs = cols[6].button("update-logs")
        reinit = cols[7].button("re-init")

        if cat_df:
            ss.page = "df-categorized"
        elif uncat_df:
            ss.page = "df-uncategorized"
        elif update_logs:
            ss.page = "update-logs"

        if reinit:
            initialize()

    if home_button:
        ss.page = "home"
    elif catz_button:
        ss.page = "categorize"
    elif trends_button:
        ss.page = "trends"
    elif manager_button:
        ss.page = "manager"

    st.markdown("---")


def main() -> None:

    # it session state not initialized, get all needed data into state
    if not ss.initialized:
        initialize()

    if ss.page == "home":
        home_page()

    elif ss.page == "categorize":
        categorized_trans()

    elif ss.page == "trends":
        display_trends()

    elif ss.page == "manager":
        _navbar()
        manager_page(ss)

    elif ss.page == "df-categorized":
        _navbar()
        st.text("categorized")
        st.write(ss.catted_trans_df)

    elif ss.page == "df-uncategorized":
        _navbar()
        st.text("uncategorized")
        st.write(ss.uncatted_trans_df)

    elif ss.page == "update-logs":
        _navbar()
        st.write(ss.update_logs)

    ss.sync()


if __name__ == "__main__":
    main()
