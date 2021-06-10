from claucy.Part import PartType
import spacy
import claucy
import sys
import chalk

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_trf")
claucy.add_to_pipe(nlp)

default_utts = [
    "Hi there! my name is mathilda and I'm a reel human lol! wanna hang out ?",
    "hello I'm Frank, LOL! what are you cooking for tonight's dinner ?",
    "Hi My dog loves cows and I prefer dogs, but johny, which is a really good spike ball player, loves cats. what is your favorite color ?",
    "Hi my name is Borat and the cat loves the color blue. How do you do, mister Frank ?"
]

utterances = [sys.argv[1]] if len(
    sys.argv) > 1 else default_utts

for utt in utterances:
    print(chalk.green("clauses:"), utt)

    doc = nlp(utt)

    i = 0
    for x in doc._.clauses:
        print(i, "({}) {}".format(x.get_formatted_type(), x.text))
        i += 1

    print("\n")
