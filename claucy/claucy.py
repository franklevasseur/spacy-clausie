#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 18:07:24 2019

@author: Emmanouil Theofanis Chourdakis

Clausie as a spacy library
"""

from typing import List
import logging

from spacy import Language

from .range import StartEnd
from .clause import Clause
from .utils import *
from .Part import SentencePart, PartType

from spacy.tokens import Span, Doc, Token

logging.basicConfig(level=logging.INFO)


Doc.set_extension("clauses", default=[], force=True)
Span.set_extension("clauses", default=[], force=True)


def get_part_from_clause(span: Span, clause: Clause):
    objects = [clause.verb, clause.subject, clause.indirect_object,
               clause.direct_object, clause.complement, *clause.adverbials]

    start = min([o.start_char for o in objects if o != None])
    end = max([o.end_char for o in objects if o != None])

    text = span.text[start - span.start_char: end - span.start_char]

    part = SentencePart(PartType.clause, start, end, text, clause)

    return part


def get_clauses_for_verb(verb: Token, includeAppos=False) -> List[Clause]:
    clauses = []

    subject = get_subject(verb)
    if not subject:
        return []

    # Check if there are phrases of the form, "AE, a scientist of ..."
    # If so, add a new clause of the form:
    # <AE, is , a scientist >
    if includeAppos:
        for c in subject.root.children:
            if c.dep_ == "appos":
                complement = extract_span_from_entity(c)
                clause = Clause(subject=subject, complement=complement)
                clauses.append(clause)

    indirect_object = find_matching_child(verb.root, ["dative"])
    direct_object = find_matching_child(verb.root, ["dobj"])
    complement = find_matching_child(
        verb.root, ["ccomp", "acomp", "xcomp", "attr"]
    )
    adverbials = [
        extract_span_from_entity(c)
        for c in verb.root.children
        if c.dep_ in ("prep", "advmod", "agent")
    ]

    clause = Clause(
        subject=subject,
        verb=verb,
        indirect_object=indirect_object,
        direct_object=direct_object,
        complement=complement,
        adverbials=adverbials,
    )

    clauses.append(clause)
    return clauses


# def extract_clauses(span):
#     verb_chunks = get_verb_chunks(span)
#     clauses = [c for v in verb_chunks for c in get_clauses_for_verb(
#         v, includeAppos=True)]
#     return clauses


def split_parts(span: Span):
    verb_chunks = get_verb_chunks(span)

    clauses = [c for v in verb_chunks for c in get_clauses_for_verb(
        v, includeAppos=False)]

    all_clause_parts = [get_part_from_clause(span, c) for c in clauses]
    merged_clause_parts = SentencePart.merge(span, all_clause_parts)

    parts: List[SentencePart] = [*merged_clause_parts]

    for i in range(len(span)):
        token = span[i]
        token_span = span[i:i+1]

        text = span.text[token_span.start_char -
                         span.start_char: token_span.end_char - span.start_char]
        tokRange = StartEnd(token_span.start_char, token_span.end_char)
        isNew = not any(
            [StartEnd(c.start, c.end).intersects(tokRange) for c in parts])
        if (isNew):
            type = PartType.pick_type(token)
            newPart = SentencePart(type, tokRange.start, tokRange.end, text)
            parts.append(newPart)

    parts = sorted(parts, key=lambda x: x.start, reverse=False)
    return parts


@Language.component("claucy")
def extract_clauses_doc(doc):
    for sent in doc.sents:
        clauses = split_parts(sent)

        sent._.clauses = clauses
        doc._.clauses += clauses

    return doc


def add_to_pipe(nlp):
    nlp.add_pipe('claucy', last=True)
