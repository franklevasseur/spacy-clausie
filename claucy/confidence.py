from typing import List
from .Part import SentencePart, PartType


def compute_confidence(parts: List[SentencePart]):
    n_toks = sum([len(p.span) for p in parts])

    untagged_parts = [x for x in filter(lambda p: p.type == PartType.other, parts)]
    n_untagged_toks = sum([len(p.span) for p in untagged_parts])

    return (n_toks - n_untagged_toks) / n_toks