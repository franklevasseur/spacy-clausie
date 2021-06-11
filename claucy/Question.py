

import typing
from spacy.tokens import Span


class Question:

    def __init__(self,
                 subject: typing.Optional[Span] = None,
                 verb: typing.Optional[Span] = None,
                 aux: typing.Optional[Span] = None):
        self.subject = subject
        self.verb = verb
        self.aux = aux
