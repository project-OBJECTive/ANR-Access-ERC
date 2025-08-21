import pandas as pd
from ontology import properties as p
from utils import to_literal

def populate_entity(uri: str, type: str, label: str | None, comment: str = None, language: str = None) -> list[tuple[str, str, str]]:
    to_return = [(uri, p.type, type)]
    if label is not None and pd.notna(label): to_return.append((uri, p.label, to_literal(label, language)))
    if comment is not None and pd.notna(comment): to_return.append((uri, p.comment, to_literal(comment, language)))
    return to_return