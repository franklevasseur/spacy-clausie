from typing import List
from claucy.Part import PartType, SentencePart
import chalk


def Color(code): return '\033[{}m'.format(code)


NC = '\033[0m'  # No Color


def get_chalk(clause):
    if clause.type == PartType.question:
        return chalk.cyan
    if clause.type == PartType.clause:
        return chalk.yellow
    if clause.type == PartType.coordinating_conjunction:
        return chalk.blue
    if clause.type == PartType.marker:
        return lambda string: "{}{}{}".format(Color('1;31'), string, NC)
    if clause.type == PartType.interjection:
        return chalk.green
    if clause.type == PartType.other:
        return chalk.magenta
    return lambda x: x


def format_clause(utt: str, parts: List[SentencePart], conf=1):
    formatted = ""

    idx = 0
    for c in parts:
        if c.type == PartType.punctuation:
            formatted += c.span.text
            idx = c.end_char + 1
            continue

        before = utt[idx:c.start_char]
        content = utt[c.start_char:c.end_char]

        chalker = get_chalk(c)

        open_sq_br = chalker('[')
        close_sq_br = chalker(']')

        open_par = chalker('(')
        close_par = chalker(')')

        close_type = chalker(c.get_formatted_type())

        formatted += f'{before} {open_sq_br}{content}{close_sq_br}{open_par}{close_type}{close_par}'

        idx = c.end_char + 1

    after = utt[idx:]
    formatted += after

    formatted_conf = "{:.2f}".format(conf)
    return "({}){}".format(chalk.bold(formatted_conf), formatted)
