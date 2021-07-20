"""Streamlit spending tracker app."""
import os
import yaml
import pandas as pd
import streamlit as st
from SessionState import get_state
from os import path
from data_setup import raw_data
from common.constants import *

st.set_page_config(layout="wide", page_title="Spending Tracker")

ss = get_state()


def lookup_description(original_description):
    # contain to hold any description matches
    # some descriptions might be subsets of other
    matched = []

    # if any phrases in identity_phrases are substring of original_description
    # pretty descript is phrase
    for phrase in ss.descr['identity_phrases']:
        if phrase.lower() in original_description.lower():
            matched.append(phrase.title())

    for phrase_map in ss.descr['phrase_maps']:
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
    descr_map = load_yaml(PATH_TO_DESCRIPTION_CONF)
    new_descriptions = []
    for orig in original_descriptions:
        new_descriptions.append(lookup_description(orig, descr_map))
    return new_descriptions


def get_uncatted_trans():
    """return a batch of uncategorized transactions from raw transactions"""
    if not ss.catted_exists:
        return ss.raw_trans_df
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
        return uncategorized_df


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


def update_descr_maps(rule_txt, rule_type):
    """adds the new description to ss and overwrites yamls"""

    if rule_type == "identity":
        format_txt = rule_txt.replace("'", "")
        ss.descr["identity_phrases"] += [format_txt]

    elif rule_type == "phrase_map":
        new_phrase = {}

        split_kv = rule_txt.split(":")
        new_phrase["key_phrase"] = split_kv[0].replace("'", "").strip()
        new_phrase["description"] = split_kv[1].replace("'", "").strip()

        ss.descr["phrase_maps"] += [new_phrase]

    # overwrite yaml file with updated state
    with open(PATH_TO_DESCRIPTION_CONF, "w") as f:
        yaml.dump(ss.descr, f)


def descr_adder_wigit():
    cols = st.beta_columns((3, 1, 10))
    descr_rule_def = cols[0].text_input("New Description Rule")
    cols[1].markdown("")
    cols[1].markdown("")
    apply_descript_rule = cols[1].button("Apply")
    st.markdown("")

    # if button clicked
    if apply_descript_rule:
        rule_type = "phrase_map" if ":" in descr_rule_def else "identity"
        update_descr_maps(descr_rule_def, rule_type)


def categorized_transactions():
    """categorize a batch of new transactions and append them to categorized"""
    _navbar()

    # get total number of uncategorized transactions
    n_uncatted = len(ss.uncatted_trans_df)

    st.title(f"You have {n_uncatted} uncategorized transactions")
    st.title("")

    descr_adder_wigit()

    batch_size = 5
    batch_indicies = ss.uncatted_trans_df.index[0:batch_size]
    uncatted_batch = ss.uncatted_trans_df.iloc[batch_indicies, :]

    uncatted_batch["description"] = uncatted_batch["original_description"].apply(lambda x: lookup_description(x))

    # get total number of columns needed to display data and wigits
    total_ncols = len(uncatted_batch.columns) + 2

    # headers for columns
    header_cols = st.beta_columns(total_ncols)

    # write column headers
    for i in range(len(uncatted_batch.columns)):
        header_cols[i].markdown(uncatted_batch.columns[i].upper())

    header_cols[total_ncols - 2].markdown("CATEGORY")
    header_cols[total_ncols - 1].markdown("SUB CATEGORY")

    # container for category values
    assigned_cats = ["None"] * batch_size
    assigned_subcats = ["None"] * batch_size

    # write transaction info into grid
    for index, row in uncatted_batch.reset_index(drop=True).iterrows():
        value_cols = st.beta_columns(total_ncols)
        for i in range(len(row.values)):
            value_cols[i].text(row.values[i])

        # get suggested categoies based on this description
        sugg_cat, sugg_subcat = lookup_category(row["description"])

        selected_category = value_cols[total_ncols - 2].selectbox(
            label="",
            options=list(ss.cats.keys()),
            key=f"cat_{index}",
            index=sugg_cat,
        )
        assigned_cats[index] = selected_category

        selected_subcategory = value_cols[total_ncols - 1].selectbox(
            label="",
            options=ss.cats[assigned_cats[index]],
            key=f"subcat_{index}",
            index = sugg_subcat,
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

        # remove categorized transactions from uncategorized
        ss.uncatted_trans_df = ss.uncatted_trans_df.drop(batch_indicies)

        # overwrite file with saved transactions
        ss.catted_trans_df.to_csv(PATH_TO_CATEGORIZED, index=False)

        # update description categoryo map
        ss.descr_cat_map = get_descr_cat_map()


def display_trends():
    _navbar()
    st.text("catted_trans_df")
    st.write(ss.catted_trans_df.head())
    st.text("uncatted_trans_df")
    st.write(ss.uncatted_trans_df.head())
    st.text("cats")
    st.write(ss.cats)
    st.text("descr")
    st.write(ss.descr)
    st.text("descr_cats_map")
    st.write(ss.descr_cat_map)


def home_page():
    _navbar()
    st.write(os.listdir("."))
    st.write("Welcome to your spending tracker!")


def _navbar() -> None:
    """Display navbar."""
    cols = st.beta_columns(8)

    home_button = cols[0].button("Home")
    catz_button = cols[1].button("Categorize")
    trends_button = cols[2].button("Trends")
    cat_df = cols[3].button("df-categorized")
    uncat_df = cols[4].button("df-uncategorized")

    if home_button:
        ss.page = "home"
    if catz_button:
        ss.page = "categorize"
    if trends_button:
        ss.page = "trends"
    if cat_df:
        ss.page = "df-categorized"
    if uncat_df:
        ss.page = "df-uncategorized"

    st.markdown("---")


def get_descr_cat_map():
    """gets a mapping from pretty descriptions to most common category substring
    previously categorized transactions"""

    descript_cat_map = {}

    if ss.catted_exists:
        # get count of category/subcategory per description
        cat_count = ss.catted_trans_df.groupby(
            ["description", "category", "subcategory"],
            as_index = False
        ).date.count()

        cat_count.rename(columns={"date":"count"}, inplace=True)

        # sort by cat count descending
        cat_count.sort_values(["description", "count"], ascending = [True, False], inplace = True)

        # row order partitioned by description
        cat_count["row_num"] = cat_count.groupby("description").cumcount() + 1

        # first row
        first_row_df = cat_count.loc[cat_count["row_num"] == 1, ["description", "category", "subcategory"]]

        for index, row in first_row_df.iterrows():
            descript_cat_map[row["description"]] = {
                "category": row["category"],
                "subcategory": row["subcategory"]
                }

    return descript_cat_map


def main() -> None:

    reinit = st.button("re-init")

    # it session state not initialized, intialize data frames in session state
    if not ss.initialized or reinit:
        ss.update_logs = raw_data.update()
        ss.page = "home"
        ss.initialized = True
        ss.raw_trans_df = load_raw_trans()
        ss.catted_exists = os.path.exists(PATH_TO_CATEGORIZED_TRANSACT)
        ss.catted_trans_df = load_catted_trans()
        ss.uncatted_trans_df = get_uncatted_trans()
        ss.cats = load_yaml(PATH_TO_CATEGORIES_CONF)
        ss.descr = load_yaml(PATH_TO_DESCRIPTION_CONF)
        ss.descr_cat_map = get_descr_cat_map()
        ss.raw_trans_df = None

    if ss.page == "home":
        home_page()

    elif ss.page == "categorize":
        categorized_transactions()

    elif ss.page == "trends":
        display_trends()

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
        st.text("update-logs")
        st.write(ss.update_logs)

    ss.sync()


if __name__ == "__main__":
    main()