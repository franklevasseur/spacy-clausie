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

QUESTION_WORDS = [
    'how',
    'what',
    'when',
    'where',
    'who',
    'why'
]


def get_part_from_clause(span: Span, clause: Clause):

    objects = [clause.verb, clause.subject, clause.indirect_object,
               clause.direct_object, clause.complement, *clause.adverbials]

    start_tok = min([o.start for o in objects if o != None])
    end_tok = max([o.end for o in objects if o != None])

    if clause.verb_question != None:

        previous_tokens = span[start_tok -
                               span.start:clause.verb_question.start - span.start]

        def is_question_word(t): return t.text.lower() in QUESTION_WORDS
        preceding_question_words_filter = filter(
            is_question_word, previous_tokens)
        preceding_question_words = [x for x in preceding_question_words_filter]

        if len(preceding_question_words) == 0:
            start_tok = clause.verb_question.start
        else:
            last_question_word = max(
                preceding_question_words, key=lambda t: t.i)
            start_tok = last_question_word.i

    new_span = span[start_tok - span.start: end_tok - span.start]

    part_type = PartType.question if contains_question(
        new_span) else PartType.clause

    part = SentencePart(part_type, new_span.start_char,
                        new_span.end_char, new_span.text, clause)

    return part


def get_clauses_for_verb(verb: Span, includeAppos=False) -> List[Clause]:
    clauses = []

    is_question = is_verb_question(verb)
    subject = get_subject(verb)

    if not subject and is_question and verb.root.pos_ == 'AUX' and verb.root.head.pos_ == 'VERB':
        head_i = verb.root.head.i - verb.sent.start
        [head_clause] = get_clauses_for_verb(verb.sent[head_i: head_i + 1])
        head_clause.verb_question = verb
        return [head_clause]

    # TODO
    # accepts sentences like:
    # [x] "trying to get to NY" with no subject
    # [ ] "Just spoke with your Retentio Dept to lower my monthly bill" (not covered yet)
    verb_is_first = verb.root == verb.sent[0]
    if not subject and not verb_is_first:
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

    # print(clause.to_propositions(as_text=True, inflect=None))

    clauses.append(clause)
    return clauses


# def extract_clauses(span):
#     verb_chunks = get_verb_chunks(span)
#     clauses = [c for v in verb_chunks for c in get_clauses_for_verb(
#         v, includeAppos=True)]
#     return clauses


def split_parts(span: Span):

    # if (contains_question(span)):
    #     return [SentencePart(PartType.question, span.start_char, span.end_char, span.text)]

    verb_chunks = get_verb_chunks(span)

    clauses = [c for v in verb_chunks for c in get_clauses_for_verb(
        v, includeAppos=False)]

    uniq_clauses = []  # rm duplicate clauses with same verb
    for c in clauses:
        already_added_clause = next(
            filter(lambda uc: uc.verb == c.verb, uniq_clauses), None)
        if already_added_clause == None:
            uniq_clauses.append(c)
            continue

        if already_added_clause.verb_question == None and c.verb_question != None:
            uniq_clauses.remove(already_added_clause)
            uniq_clauses.append(c)
            continue

    all_clause_parts = [get_part_from_clause(span, c) for c in uniq_clauses]
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
            newPart = SentencePart(type, tokRange.start,
                                   tokRange.end, text, token=token)
            parts.append(newPart)

    parts = sorted(parts, key=lambda x: x.start, reverse=False)
    # parts = [x for x in filter(
    #     lambda p: p.type != PartType.punctuation, parts)]

    i = 1
    while i < len(parts):
        previous_part = parts[i - 1]
        current_part = parts[i]

        if (current_part.type == PartType.other and previous_part.type == PartType.other):
            parts[i - 1] = SentencePart(PartType.other, previous_part.start, current_part.end, "{} {}".format(
                previous_part.text, current_part.text))
            del parts[i]
            continue

        i += 1

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
