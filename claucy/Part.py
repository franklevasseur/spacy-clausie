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

                start_char = min(first.start_char, second.start_char)
                end_char = max(first.end_char, second.end_char)

                start = min(first.start, second.start)
                end = max(first.end, second.end)

                text = span[start - span.start: end - span.start]

                merged_type = PartType.merge_types(first, second)
                mergedPart = SentencePart(merged_type, StartEnd(start_char, end_char), StartEnd(
                    start, end), text, first.clause or second.clause)

                merged.append(mergedPart)

                i = 0
                pairs = getPairs(len(merged))
                continue

            i += 1

        return merged

    @staticmethod
    def isSuperposed(first: SentencePart, second: SentencePart):
        range1 = StartEnd(first.start_char, first.end_char)
        range2 = StartEnd(second.start_char, second.end_char)
        return range1.intersects(range2)

    def __init__(self, part_type: PartType, char_range: StartEnd, tok_range: StartEnd, span: Span, clause: Clause = None, token: Token = None):
        self.type = part_type
        self.start_char = char_range.start
        self.end_char = char_range.end

        self.start = tok_range.start
        self.end = tok_range.end

        self.span = span

        self.clause = clause
        self.token = token

    def get_formatted_type(self):
        if self.type == PartType.clause:
            return "{}-{}".format(self.type, self.clause.get_clause_type())

        if self.type == PartType.other and self.token:
            return "{}-{}".format(self.type, self.token.dep_)

        return str(self.type)


class PartType(Enum):
    question = 'q'
    clause = 'clause'
    interjection = 'intj'
    coordinating_conjunction = 'cc'
    marker = 'mark'
    punctuation = 'punct'
    other = 'other'

    def is_same(self, other: PartType):
        return self.value == other.value

    def get_order(self):
        if self.is_same(PartType.question):
            return 0

        if self.is_same(PartType.clause):
            return 1

        if self.is_same(PartType.interjection):
            return 2

        if self.is_same(PartType.coordinating_conjunction):
            return 3

        if self.is_same(PartType.marker):
            return 4

        if self.is_same(PartType.punctuation):
            return 5

        if self.is_same(PartType.other):
            return 6

        return -1

    @ staticmethod
    def merge_types(first: SentencePart, second: SentencePart):
        first_type = first.type
        second_type = second.type
        return min(first_type, second_type, key=lambda x: x.get_order())

    @ staticmethod
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
        return self.value
