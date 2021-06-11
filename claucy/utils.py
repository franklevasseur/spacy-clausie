from typing import Tuple
from spacy.tokens import Span
from spacy.matcher import Matcher


def extract_span_from_entity(token):
    ent_subtree = sorted([c for c in token.subtree], key=lambda x: x.i)
    return Span(token.doc, start=ent_subtree[0].i, end=ent_subtree[-1].i + 1)


def extract_span_from_entity_no_cc(token):
    ent_subtree = sorted(
        [token] + [c for c in token.children if c.dep_ not in ["cc", "conj", "prep"]],
        key=lambda x: x.i,
    )
    return Span(token.doc, start=ent_subtree[0].i, end=ent_subtree[-1].i + 1)


def extract_ccs_from_entity(token):
    entities = [extract_span_from_entity_no_cc(token)]
    for c in token.children:
        if c.dep_ in ["conj", "cc"]:
            entities += extract_ccs_from_entity(c)
    return entities


def extract_ccs_from_token_at_root(span):
    if span is None:
        return []
    else:
        return extract_ccs_from_token(span.root)


def extract_ccs_from_token(token):
    if token.pos_ in ["NOUN", "PROPN", "ADJ"]:
        children = sorted(
            [token]
            + [
                c
                for c in token.children
                if c.dep_ in ["advmod", "amod", "det", "poss", "compound"]
            ],
            key=lambda x: x.i,
        )
        entities = [Span(token.doc, start=children[0].i,
                         end=children[-1].i + 1)]
    else:
        entities = [Span(token.doc, start=token.i, end=token.i + 1)]
    for c in token.children:
        if c.dep_ == "conj":
            entities += extract_ccs_from_token(c)
    return entities


def convert_clauses_to_text(propositions, inflect, capitalize):
    proposition_texts = []
    for proposition in propositions:
        span_texts = []
        for span in proposition:

            token_texts = []
            for token in span:
                token_texts.append(inflect_token(token, inflect))

            span_texts.append(" ".join(token_texts))
        proposition_texts.append(" ".join(span_texts))

    if capitalize:  # Capitalize and add a full stop.
        proposition_texts = [
            text.capitalize() + "." for text in proposition_texts]

    return proposition_texts


def inflect_token(token, inflect):
    if (
        inflect
        and token.pos_ == "VERB"
        and "AUX" not in [tt.pos_ for tt in token.lefts]
        # t is not preceded by an auxiliary verb (e.g. `the birds were ailing`)
        and token.dep_ != "pcomp"
    ):  # t `dreamed of becoming a dancer`
        return str(token._.inflect(inflect))
    else:
        return str(token)


def get_verb_matches(span):
    # 1. Find verb phrases in the span
    # (see mdmjsh answer here: https://stackoverflow.com/questions/47856247/extract-verb-phrases-using-spacy)

    verb_matcher = Matcher(span.vocab)
    verb_matcher.add("Auxiliary verb phrase aux-verb",
                     [[{"POS": "AUX"}, {"POS": "VERB"}]])
    verb_matcher.add("Auxiliary verb phrase", [[{"POS": "AUX"}]])
    verb_matcher.add("Verb phrase", [[{"POS": "VERB"}]])

    return verb_matcher(span)


def get_verb_chunks(span):
    matches = get_verb_matches(span)

    # Filter matches (e.g. do not have both "has won" and "won" in verbs)
    verb_chunks = []
    for match in [span[start:end] for _, start, end in matches]:
        if match.root not in [vp.root for vp in verb_chunks]:
            verb_chunks.append(match)
    return verb_chunks


def is_verb_question(verb):

    for c in verb.root.children:
        if c.dep_ in ["nsubj", "nsubjpass", "expl"]:
            subject = extract_span_from_entity(c)
            if verb.start_char < subject.start_char:
                return True

    if verb.root.dep_ == 'aux' and verb.root.head.pos_ == 'VERB':
        for c in verb.root.head.children:
            if c.dep_ in ["nsubj", "nsubjpass", "expl"]:
                subject = extract_span_from_entity(c)
                if verb.start_char < subject.start_char:
                    return True

    return False


def contains_question(span):
    verbs = get_verb_chunks(span)
    return any([is_verb_question(verb) for verb in verbs])


def get_subject(verb) -> Span:
    for c in verb.root.children:
        if c.dep_ in ["nsubj", "nsubjpass", "expl"]:
            subject = extract_span_from_entity(c)
            return subject

    root = verb.root
    while root.dep_ in ["conj", "cc", "advcl", "acl", "ccomp", "ROOT"]:
        for c in root.children:
            if c.dep_ in ["nsubj", "nsubjpass", "expl"]:
                subject = extract_span_from_entity(c)
                return subject

            if c.dep_ in ["acl", "advcl"]:
                subject = find_verb_subject(c)
                subject = extract_span_from_entity(
                    subject) if subject else None
                return subject

        # Break cycles
        if root == verb.root.head:
            break
        else:
            root = verb.root.head

    for c in root.children:
        if c.dep_ in ["nsubj", "nsubj:pass", "nsubjpass"]:
            subject = extract_span_from_entity(c)
            return subject

    return None


def find_matching_child(root, allowed_types):
    for c in root.children:
        if c.dep_ in allowed_types:
            return extract_span_from_entity(c)
    return None


def find_verb_subject(v):
    """
    Returns the nsubj, nsubjpass of the verb. If it does not exist and the root is a head,
    find the subject of that verb instead.
    """
    if v.dep_ in ["nsubj", "nsubjpass", "nsubj:pass"]:
        return v
    # guard against infinite recursion on root token
    elif v.dep_ in ["advcl", "acl"] and v.head.dep_ != "ROOT":
        return find_verb_subject(v.head)

    for c in v.children:
        if c.dep_ in ["nsubj", "nsubjpass", "nsubj:pass"]:
            return c
        elif c.dep_ in ["advcl", "acl"] and v.head.dep_ != "ROOT":
            return find_verb_subject(v.head)
