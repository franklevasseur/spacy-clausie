from __future__ import annotations
from enum import Enum
from typing import List
from spacy.tokens import Span, Token

from .range import StartEnd
from .clause import Clause
from .pairs import getPairs


class SentencePart:

    @staticmethod
    def merge(span: Span, parts: List[SentencePart]) -> List[SentencePart]:
        merged = [*parts]

        pairs = getPairs(len(merged))
        i = 0
        while i < len(pairs):

            p = pairs[i]

            first = merged[p[0]]
            second = merged[p[1]]

            if SentencePart.isSuperposed(first, second):
                merged.remove(first)
                merged.remove(second)

                start = min(first.start, second.start)
                end = max(first.end, second.end)
                text = span.text[start -
                                 span.start_char: end - span.start_char]

                merged_type = PartType.merge_types(first, second)
                mergedPart = SentencePart(
                    merged_type, start, end, text, first.clause or second.clause)

                merged.append(mergedPart)

                i = 0
                pairs = getPairs(len(merged))
                continue

            i += 1

        return merged

    @staticmethod
    def isSuperposed(first: SentencePart, second: SentencePart):
        range1 = StartEnd(first.start, first.end)
        range2 = StartEnd(second.start, second.end)
        return range1.intersects(range2)

    def __init__(self, type: PartType, start: int, end: int, text: str, clause: Clause = None, token: Token = None):
        self.type = type
        self.start = start
        self.end = end
        self.text = text
        self.clause = clause
        self.token = token

    def get_formatted_type(self):
        if self.type == PartType.clause:
            return "{}-{}".format(self.type, self.clause.get_clause_type())

        if self.type == PartType.other and self.token:
            return "{}-{}".format(self.type, self.token.dep_)

        return str(self.type)


class PartType(Enum):
    question = (0, 'q')
    clause = (1, 'clause')
    interjection = (2, 'intj')
    coordinating_conjunction = (3, 'cc')
    marker = (4, 'mark')
    punctuation = (5, 'punct')
    other = (6, 'other')

    @staticmethod
    def merge_types(first: SentencePart, second: SentencePart):
        first_type = first.type
        second_type = second.type
        return min(first_type, second_type, key=lambda x: x.value[0])

    @staticmethod
    def pick_type(tok: Token):
        if (tok.dep_ == 'intj'):
            return PartType.interjection

        if (tok.dep_ == 'cc'):
            return PartType.coordinating_conjunction

        if (tok.dep_ == 'mark'):
            return PartType.marker

        if (tok.dep_ == 'punct'):
            return PartType.punctuation

        return PartType.other

    def __str__(self):
        return self.value[1]
