import yaml
from common.constants import *
from collections import OrderedDict


def load_yaml(file_path: str) -> dict:
    with open(file_path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def save_yaml(file_path: str, values: dict) -> None:
    with open(file_path, "w") as f:
        yaml.dump(values, f)


def sort_cats() -> None:
    cats = load_yaml(PATH_TO_CATEGORIES_CONF)
    sorted_cats = {}

    for key in sorted(cats.keys()):
        sorted_cats[key] = sorted(cats[key])

    # make sure everything is still in the sorted dictionary before overwriting
    assert len(cats) == len(sorted_cats)
    assert sorted(cats.keys()) == sorted(sorted_cats.keys())
    for k in cats.keys():
        assert sorted(cats[k]) == sorted(sorted_cats[k])

    save_yaml(PATH_TO_CATEGORIES_CONF, sorted_cats)


def to_snake(txt: str) -> str:
    words = txt.lower().split(" ")
    return "_".join(words)

