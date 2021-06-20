import pandas as pd
import streamlit as st
import os
from app.describer.describer import describer
from categories import CATEGORIES

st.set_page_config(layout="wide", page_title="Spending Tracker")

# @st.cache(allow_output_mutation=True, show_spinner=True, suppress_st_warning=False)

TRANS_KEY_COLS = ["date", "original_description", "amount"]

CONFIG = get_config()

def to_snake(txt):
    words = txt.lower().split(" ")
    return "_".join(words)


def get_trans_keys(df):
    return df[TRANS_KEY_COLS].drop_duplicates()


def get_net_amount(row):
    if row['transaction_type'] == 'debit':
        return row['amount']
    else:
        return row['amount'] * -1


def load_transactions(path):
    df = pd.read_csv(path)
    df.columns = [to_snake(col) for col in df.columns]
    df["amount"] = df.apply(get_net_amount, axis = 1)
    df.rename(columns = {"description": "mint_description"}, inplace = True)
    return df.drop(["transaction_type","category","labels","notes"], axis = 1)


def get_uncatted_trans():

    raw_trans = load_transactions("./data/raw/transactions.csv")

    # if catted_trans exist, get difference
    if "transactions.csv" in os.listdir("./data/categorized/"):
        catted = load_transactions("./data/categorized/transactions.csv")
        catted_keys = get_trans_keys(catted)
        catted_keys.columns = ["catted_" + col for col in catted_keys.columns]
        join_catted = raw_trans.merge(catted_keys, left_on = TRANS_KEY_COLS, right_on = catted_keys.columns, how = "left")
        uncatted_trans = join_catted[catted_keys.columns[0].isna()].drop(catted_keys.columns)
        return uncatted_trans

    else:
        return raw_trans


def categorized_transactions():
    _navbar()
    uncatted = get_uncatted_trans().head()
    df_ncols = uncatted.shape[0]
    total_ncols = df_ncols+2
    st.title(f"You have {len(uncatted)} uncategorized transactions")
    st.title("")

    # headers for columns
    header_cols = st.beta_columns(total_ncols)

    for i in range(len(uncatted.columns)):
        header_cols[i].markdown(uncatted.columns[i].upper())

    header_cols[total_ncols - 2].markdown("DESCRIPTION")
    header_cols[total_ncols - 1].markdown("CATEGORY")

    # write transaction info w dd for
    for index, row in uncatted.iterrows():
        value_cols = st.beta_columns(total_ncols)
        for i in range(len(row.values)):
            value_cols[i].text(row.values[i])

        # add text box with suggested description
        suggested_description = "desc" #get_new_description(row["mint_description"])
        suggested_category = "cat"

        value_cols[total_ncols - 2].text(suggested_description)
        value_cols[total_ncols - 1].selectbox(label = "", options = ['hi'], key = f"cat_{index}")

        st.markdown("---")


def display_trends():
    _navbar()
    st.write("This is where the trends will go")


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

    params = st.experimental_get_query_params()
    page = params.get("page", ["home"])[0]

    if page == "home":
        home_page()

    elif page == "categorize":
        categorized_transactions()

    elif page == "trends":
        display_trends()

    else:
        _navbar()
        st.write("not a page")


if __name__ == "__main__":
    _main()
