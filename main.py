import spacy
import claucy
import sys
import chalk

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")
claucy.add_to_pipe(nlp)


utt = sys.argv[1] if len(
    sys.argv) > 1 else "Hi, My dog loves cows and I prefer dogs, but johny, which is a really good spike ball player, loves cats. what is your favorite color ?"
doc = nlp(utt)

i = 0
print(chalk.green("clauses:"))
for x in doc._.clauses:
    print(i, x['part'])
    i += 1

print("\n")
print(chalk.green("logical clauses:"))
i = 0
for x in [p for c in doc._.logical_clauses for p in c.to_propositions(as_text=True, inflect=None)]:
    print(i, x)
    i += 1
