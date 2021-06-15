from claucy.confidence import compute_confidence
from format import format_clause
from claucy.Part import PartType
import spacy
import claucy
import sys
import chalk
import json

spacy.prefer_gpu()
# nlp = spacy.load("en_core_web_lg") # faster but feels sloppier
nlp = spacy.load("en_core_web_trf") # slower but feels more accurate
claucy.add_to_pipe(nlp)

default_utts = [
    # "Hi! my name is mathilda and I'm a reel human. Do you want to hang out ?", # easier
    # "Hi there! my name is mathilda and I'm a reel human lol! wanna hang out ?", # harder
    # "hello I'm Frank, LOL! what are you cooking for tonight's dinner ?",
    # "Hi My dog loves cows and I prefer dogs, but johny, which is a really good spike ball player, loves cats. what is your favorite color ?",
    # "Hi my name is Borat and the cat loves the color blue. How do you do, mister Frank ?",
    # "Hi, Does the person need to call in to confirm or just show up at the airport prior to departing time",
    # "this did not help, can you please tell me how much it is tu upgrade",
    # "I need to get from newark De to American University can you help me",
    # "I purchased a ticket for my son this summer that I never used. I am now trying to track down information on the ticket so that I can use it. Can you help?",
    # "Planning a trip to Italy anywhere from end of april to early june for 10 days",
    # "I was making a reservation using miles and somehow clicked on something midway and did not finish--how can I find it",
    # "Why is my wifi not matching up to what it should be ?",
    # "I have a reservation on thanksgiving morning and just remembered I also have an upgrade certificate. how can i apply it to my trip",
    # "I am trying to get a quote leaving Indianapolis going to Wisconsin", # spacy sees trying as the root, but with POS == 'PART'
    # "I was making a reservation using miles and somehow clicked on something midway and did not finish--how can I find it?", # spacy is confused with "...finish--how can..."
]


utterances = []
if len(sys.argv) > 1:
    utterances = [sys.argv[1]]
elif len(default_utts) > 0:
    utterances = default_utts
else:
    with open('./data/idea.json') as f:
        data = json.load(f)
        utterances = [u['utterance'] for u in data]

print(chalk.green("clauses:"))
for utt in utterances:

    doc = nlp(utt)

    parts = doc._.clauses
    conf = compute_confidence(parts)

    formatted_line = format_clause(utt, doc._.clauses, conf)
    print(formatted_line)
