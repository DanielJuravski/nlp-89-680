import codecs

import spacy
from collections import defaultdict

PEOPLE_TITLES = ["mr.", "mrs.", "ms.", "prince", "sir", "sultan", "lord"]

def extract_ent_tuples(in_file):
    ent_tuples = defaultdict(list)
    with open(in_file) as f:
        for line in f.readlines():
            arr = line.split("\t")
            senid = arr[0]
            ent1 = arr[1]
            ent2 = arr[3]
            ent_tuples[senid].append((ent1, ent2))

    return ent_tuples


def read_lines(fname):
    for line in codecs.open(fname, encoding="utf8"):
        sent_id, sent = line.strip().split("\t")
        sent = sent.replace("-LRB-","(")
        sent = sent.replace("-RRB-",")")
        yield sent_id, sent


def check(gold_ent, sent, sent_id):
    found = False
    g_arr = gold_ent.split()
    if g_arr[0].lower() in PEOPLE_TITLES:
        gold_ent = " ".join(g_arr[1:])

    pos = "none"
    for ne in sent.ents:
        n_arr = ne.text.split()
        clean_ne = ""
        if n_arr[0].lower() == "the":
            clean_ne = " ".join(n_arr[1:])
        if ne.text == gold_ent or clean_ne == gold_ent:
            found = True
            pos = ne.label_
        if gold_ent[-1] == '.':
            if ne.text == gold_ent[:-1]:
                found = True
                pos = ne.label_

    if found:
        found_arr.append((gold_ent, sent_id, sent, pos))
    else:
        not_found_arr.append((gold_ent, sent_id, sent))
    return found

found_arr = []
not_found_arr = []

if __name__ == '__main__':
    in_file = "statistics/FN.txt"
    original_file = "data/Corpus.TRAIN.txt"
    ent_tuples = extract_ent_tuples(in_file)
    nlp = spacy.load('en_core_web_lg')
    good = bad = 0
    for sent_id, sent_str in read_lines(original_file):
        if sent_id in ent_tuples:
            failed_gold_ents = ent_tuples[sent_id]
            for tup in failed_gold_ents:
                sent = nlp(sent_str)
                if check(tup[0], sent, sent_id):
                    good+=1
                else:
                    bad += 1
                if check(tup[1], sent, sent_id):
                    good+=1
                else:
                    bad += 1

    all_sentids=set()
    not_found_sentids=set()
    for t in found_arr:
        g_ent, s_id, s, pos= t
        all_sentids.add(s_id)
        print("found: "+ s_id+": gold entity: " + g_ent + "  pos= " +pos)

    for t in not_found_arr:
        g_ent, s_id, s= t
        all_sentids.add(s_id)
        not_found_sentids.add(s_id)
        print("not found: "+ s_id+": gold entity: " + g_ent)

    percent = (good/float(good+bad)) * 100
    print("percent = %f" % percent)
    print ("unique sentences = " + str(len(all_sentids)))
    print ("not found unique sentences = " + str(len(not_found_sentids)))

