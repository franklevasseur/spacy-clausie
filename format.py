from claucy.Part import PartType
import chalk

Color=lambda code: '\033[{}m'.format(code)
NC='\033[0m' # No Color


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


def format_clause(utt: str, parts):
    formatted = ""

    idx = 0
    for c in parts:
        if c.type == PartType.punctuation:
            formatted += c.text
            idx = c.end + 1
            continue

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