import os
import yaml
import pandas as pd
import streamlit as st
import datetime
from app.utils import load_yaml, save_yaml, sort_cats
from common.constants import *


# takes a session state
def manager_page(ss):
    """TODO: this should take actions on the categorized transaction_data. This should also automatically
    make a backup of the categorized transaction_data and maybe descriptions. This probably requires keeping a
    separatre dictionary of the changes entered and then on saving to execute the changes there."""

    if not ss.temp_cats:
        ss.temp_cats = ss.cats.copy()

    # reformat cats for better display
    display_cats = ss.temp_cats.copy()
    for k, v in display_cats.items():
        display_cats[k] = ', '.join(v)

    st.write(display_cats)

    # ADD

    # add subcategory
    cols = st.beta_columns(10)
    cols[0].markdown("")
    cols[0].markdown("")
    apply_it = cols[0].button("Apply", key="add_cat")
    cat = cols[1].text_input("New Category")
    if apply_it:
        ss.temp_cats[cat] = [""]

    # add subcategory
    cols = st.beta_columns(10)
    cols[0].markdown("")
    cols[0].markdown("")
    apply_it = cols[0].button("Apply", key="add_subcat")
    cat = cols[1].text_input("Category", key="cat1")
    subcat = cols[2].text_input("New Subcategory")
    if apply_it:
        ss.temp_cats[cat].append(subcat)

    # REMOVE

    # remove category
    cols = st.beta_columns(10)
    cols[0].markdown("")
    cols[0].markdown("")
    apply_it = cols[0].button("Apply", key="rem_cat")
    cat = cols[1].text_input("Remove Category")
    if apply_it:
        ss.temp_cats.pop(cat)

    # remove subcategory
    cols = st.beta_columns(10)
    cols[0].markdown("")
    cols[0].markdown("")
    apply_it = cols[0].button("Apply", key="rem_subcat")
    cat = cols[1].text_input("Category", key="cat2")
    subcat = cols[2].text_input("Remove Subcategory")
    if apply_it:
        ss.temp_cats[cat].remove(subcat)

    # RENAME

    # rename category
    cols = st.beta_columns(10)
    cols[0].markdown("")
    cols[0].markdown("")
    apply_it = cols[0].button("Apply", key="rename_cat")
    cat = cols[1].text_input("Category", key="cat3")
    new_name = cols[2].text_input("Rename Category")
    if apply_it:
        ss.temp_cats[new_name] = ss.cats[cat]
        ss.temp_cats.pop(cat)

    # rename subcategory
    cols = st.beta_columns(10)
    cols[0].markdown("")
    cols[0].markdown("")
    apply_it = cols[0].button("Apply", key="rename_subcat")
    cat = cols[1].text_input("Category")
    subcat = cols[2].text_input("Subcategory")
    new_name = cols[3].text_input("Rename Subcategory")
    if apply_it:
        ss.temp_cats[cat].remove(subcat)
        ss.temp_cats[cat].append(new_name)

    # save button to write changes to disk
    cols = st.beta_columns(10)
    save_button = cols[0].button("Save Changes")
    discard_button = cols[1].button("Discard Changes")
    if save_button:
        ss.cats = ss.temp_cats
        save_yaml(PATH_TO_CATEGORIES_CONF, ss.cats)
        st.write("Save Successful!")
    elif discard_button:
        ss.temp_cats = None

