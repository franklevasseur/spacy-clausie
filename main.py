import spacy
import claucy

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_sm")
claucy.add_to_pipe(nlp)


doc = nlp("Hi, My dog loves cows and I prefer dogs, but johny, which is a really good spike ball player, loves cats. what is your favorite color ?")

for x in doc._.clauses:
    propositions = x.to_propositions(as_text=True)
    print(propositions)
