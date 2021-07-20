def load_yaml(file_path):
    with open(file_path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def to_snake(txt):
    words = txt.lower().split(" ")
    return "_".join(words)


def get_transact_keys(df):
    return df[TRANSACT_KEY_COLS].drop_duplicates()