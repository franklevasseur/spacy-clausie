from claucy.Part import PartType
import chalk


def get_chalk(clause):
    if clause.type == PartType.question:
        return chalk.cyan
    if clause.type == PartType.clause:
        return chalk.yellow
    if clause.type == PartType.coordinating_conjunction:
        return chalk.blue
    if clause.type == PartType.interjection:
        return chalk.green
    if clause.type == PartType.other:
        return chalk.magenta
    return lambda x: x


def format_clause(utt: str, parts):
    formatted = ""

    idx = 0
    for c in parts:
        before = utt[idx:c.start]
        content = utt[c.start:c.end]

        chalker = get_chalk(c)

        open_sq_br = chalker('[')
        close_sq_br = chalker(']')

        open_par = chalker('(')
        close_par = chalker(')')

        close_type = chalker(c.get_formatted_type())

        formatted += f'{before} {open_sq_br}{content}{close_sq_br}{open_par}{close_type}{close_par}'

        idx = c.end + 1

    after = utt[idx:]
    formatted += after

    return formatted
