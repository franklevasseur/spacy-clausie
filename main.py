import spacy
import claucy
import sys

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")
claucy.add_to_pipe(nlp)


utt = sys.argv[1]
doc = nlp(utt)
i = 0

print("clauses:")
for x in doc._.clauses:
    print(i, x['part'])
    i += 1
