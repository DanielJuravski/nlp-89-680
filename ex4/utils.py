import codecs
import spacy
import sys


SENT_PREFIX="sent"

OUR_RE = 'Live_In'
NER1 = 0
RE = 1
NER2 = 2

nlp = spacy.load('en')

def read_lines(fname):
    for line in codecs.open(fname, encoding="utf8"):
        sent_id, sent = line.strip().split("\t")
        sent = sent.replace("-LRB-","(")
        sent = sent.replace("-RRB-",")")
        yield sent_id, sent


def print_relations(relations, full_data, out_f):
    sorted_sen_ids = sorted([int(key[len(SENT_PREFIX):]) for key in relations.keys()])
    with open(out_f, "w") as f:
        for sen_id in sorted_sen_ids:
            senid_str = SENT_PREFIX + str(sen_id)
            sen_relations = relations[senid_str]
            for relation in sen_relations:
                relation_txt = "%s\tLive_In\t%s" % (relation[0], relation[1])
                full_sen = full_data[senid_str].text
                output_line = "%s\t%s\t(%s)\n" % (senid_str, relation_txt, full_sen)
                f.write(output_line)


def get_sorted_ids(sen_str_ids):
    sorted_ids =  sorted([int(key[len(SENT_PREFIX):]) for key in sen_str_ids])
    return [SENT_PREFIX + str(sen_id) for sen_id in sorted_ids]
