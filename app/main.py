import pandas as pd
import streamlit as st
import os
from describer import describer

# map of main categories and list of sub categories
CATEGORIES = {
    "eating & drinking out": ['delivery', 'resturant', 'coffe shops', "bars"],
    "home": ["rent", "utilities", "home items"],
    "grocery store": [],
    "entertainment media": ["movies", "music", "news", "books"],
    "amusement": [],
    "student loans": [],
    "transportation": ["uber","public"],
    "lodging": ["airbnb", "hotel"],
    "shopping": ["music", "sports", "clothing", "electronics"],
    "health": ["doctor", "pharmacy", "hygene", "gym", "therapy"],
    "travel": ["airplane"],
    "government": ["taxes", "dmv"],
    "insurance": ["renters", "auto"]
}

TRANS_KEY_COLS = ["date", "original_description", "amount"]

PATH_TO_RAW = "./data/raw/"

PATH_TO_CATEGORIZED = "./data/categorized/"

trans_describer = describer()

st.set_page_config(layout="wide", page_title="Spending Tracker")

# @st.cache(allow_output_mutation=True, show_spinner=True, suppress_st_warning=False)

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


def load_raw_transactions():
    df = pd.read_csv(PATH_TO_RAW + "transactions.csv")
    df.columns = [to_snake(col) for col in df.columns]
    df["amount"] = df.apply(get_net_amount, axis = 1)
    df.rename(columns = {"description": "mint_description"}, inplace = True)
    return df.drop(["transaction_type","category","labels","notes"], axis = 1)


def load_categorized_transactions():
    batch_paths = os.listdir(PATH_TO_CATEGORIZED)
    batch_dfs = []
    for file in [PATH_TO_CATEGORIZED + path for path in batch_paths]:
        batch_dfs.append(pd.read_csv(file))
    concat_df = pd.concat(batch_dfs)


def save_categorized_transactions(df):
    batch_paths = os.listdir(PATH_TO_CATEGORIZED)
    max_batch = max([int(x.split("_")[1].replace(".csv", "")) for x in batch_paths])
    next_batch_name = f"batch_{str(max_batch+1)}"
    df.to_csv(PATH_TO_CATEGORIZED + next_batch_name)


def get_uncatted_trans():
    """return a batch of uncategorized transactions from raw transactions"""
    raw_trans = load_raw_transactions()

    if len(os.listdir("./data/categorized/")) > 0:
        catted = load_categorized_transactions()
        catted_keys = get_trans_keys(catted)
        catted_keys.columns = ["catted_" + col for col in catted_keys.columns]
        join_catted = raw_trans.merge(catted_keys, left_on = TRANS_KEY_COLS, right_on = catted_keys.columns, how = "left")
        uncatted_trans = join_catted[catted_keys.columns[0].isna()].drop(catted_keys.columns)
        return uncatted_trans

    else:
        return raw_trans


def categorized_transactions():
    _navbar()
    batch_size = 10
    uncatted = get_uncatted_trans()
    uncatted_batch = uncatted.head(batch_size)
    df_ncols = uncatted.shape[0]
    total_ncols = df_ncols+3
    st.title(f"You have {len(uncatted)} uncategorized transactions")
    st.title("")

    # headers for columns
    header_cols = st.beta_columns(total_ncols)

    for i in range(len(uncatted.columns)):
        header_cols[i].markdown(uncatted.columns[i].upper())

    header_cols[total_ncols - 3].markdown("DESCRIPTION")
    header_cols[total_ncols - 2].markdown("CATEGORY")
    header_cols[total_ncols - 1].markdown("SUB CATEGORY")

    # container for category_values
    assigned_categories = ["None"] * batch_size
    assigned_subcategories = ["None"] * batch_size

    # write transaction info w dd for
    for index, row in uncatted.iterrows():
        value_cols = st.beta_columns(total_ncols)
        for i in range(len(row.values)):
            value_cols[i].text(row.values[i])

        suggested_description = trans_describer.get_pretty_description(row["mint_description"])
        #suggested_category =

        value_cols[total_ncols - 3].text(suggested_description)

        selected_category = value_cols[total_ncols - 2].selectbox(label = "", options = list(CATEGORIES.keys()), key = f"cat_{index}")
        assigned_categories[index] = selected_category

        selected_subcategy = value_cols[total_ncols - 1].selectbox(label = "", options = CATEGORIES[assigned_categories[index]], key = f"subcat_{index}")
        assigned_subcategories[index] = selected_subcategy

        st.markdown("---")

    submit = st.button("Submit and Proceed")

    if submit:
        #uncatted
        st.text("saving")


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
