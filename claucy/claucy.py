#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 18:07:24 2019

@author: Emmanouil Theofanis Chourdakis

Clausie as a spacy library
"""

import spacy
import logging

from typing import List, Tuple
from spacy import Language

from .range import StartEnd
from .clause import Clause
from .utils import *

from spacy.tokens import Span, Doc
from spacy.matcher import Matcher

logging.basicConfig(level=logging.INFO)


Doc.set_extension("clauses", default=[], force=True)
Span.set_extension("clauses", default=[], force=True)

Doc.set_extension("logical_clauses", default=[], force=True)
Span.set_extension("logical_clauses", default=[], force=True)


def get_verb_info(span, verb):
    subject = get_subject(verb)
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

    objects = [verb, subject, indirect_object,
               direct_object, complement, *adverbials]

    start = min([o.start_char for o in objects if o != None])
    end = max([o.end_char for o in objects if o != None])

    part = span.text[start - span.start_char: end - span.start_char]
    return {
        'verb': verb,
        'subject': subject,
        'start': start,
        'end': end,
        'part': part
    }


def getPairs(n):
    pairs: List[Tuple[int, int]] = []
    for i in range(n):
        for j in range(i, n):
            if i == j:
                continue

            pairs.append((i, j))
    return pairs


def isSuperposed(first, second):
    range1 = StartEnd(first['start'], first['end'])
    range2 = StartEnd(second['start'], second['end'])
    return range1.intersects(range2)


def removeSuperpositions(span, verb_infos):
    cleaned = [*verb_infos]
    n = len(verb_infos)
    pairs = getPairs(n)

    for p in pairs:
        first = verb_infos[p[0]]
        second = verb_infos[p[1]]

        if isSuperposed(first, second):
            cleaned.remove(first)
            cleaned.remove(second)

            start = min(first['start'], second['start'])
            end = max(first['end'], second['end'])
            cleaned.append({
                'start': start,
                'end': end,
                'part': span.text[start - span.start_char: end - span.start_char]
            })

    return cleaned


def split_clauses(span):
    verb_chunks = get_verb_chunks(span)
    all_verb_info = [get_verb_info(span, verb) for verb in verb_chunks]

    cleaned = removeSuperpositions(span, all_verb_info)

    for i in range(len(span)):
        tok = span[i:i+1]

        part = span.text[tok.start_char -
                         span.start_char: tok.end_char - span.start_char]
        tokRange = StartEnd(tok.start_char, tok.end_char)
        isNew = not any(
            [StartEnd(c['start'], c['end']).intersects(tokRange) for c in cleaned])
        if (isNew):
            cleaned.append({
                'start': tokRange.start,
                'end': tokRange.end,
                'part': part
            })

    clauses = sorted(cleaned, key=lambda x: x['start'], reverse=False)
    return clauses


def extract_logical_clauses(span):
    clauses = []

    verb_chunks = get_verb_chunks(span)
    for verb in verb_chunks:

        subject = get_subject(verb)
        if not subject:
            continue

        # Check if there are phrases of the form, "AE, a scientist of ..."
        # If so, add a new clause of the form:
        # <AE, is , a scientist >
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


@Language.component("claucy")
def extract_clauses_doc(doc):
    for sent in doc.sents:
        clauses = split_clauses(sent)
        logical_clauses = extract_logical_clauses(sent)

        sent._.clauses = clauses
        doc._.clauses += clauses

        sent._.logical_clauses = logical_clauses
        doc._.logical_clauses += logical_clauses

    return doc


def add_to_pipe(nlp):
    nlp.add_pipe('claucy', last=True)


if __name__ == "__main__":
    import spacy

    nlp = spacy.load("en")
    add_to_pipe(nlp)

    doc = nlp(
        # "Chester is a banker by trade, but is dreaming of becoming a great dancer."
        " A cat , hearing that the birds in a certain aviary were ailing dressed himself up as a physician , and , taking his cane and a bag of instruments becoming his profession , went to call on them ."
    )

    print(doc._.clauses)
    for clause in doc._.clauses:
        print(clause.to_propositions(as_text=True, capitalize=True))
    print(doc[:].noun_chunks)
