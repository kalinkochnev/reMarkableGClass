from typing import List

def filter_get(attr: str, value: str, items: List[dict]):
    """Returns the first dictionary in a list that has the expected key and value"""
    for item in items:
        if attr not in item.keys():
            pass
        if item[attr] == value:
            return item
    return None