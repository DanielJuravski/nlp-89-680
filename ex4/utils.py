import codecs
import spacy_parser
import pickle
import spacy
import sys


SENT_PREFIX="sent"

OUR_RE = 'Live_In'
NER1 = 0
RE = 1
NER2 = 2

nlp = spacy.load('en_core_web_lg')

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

def get_senid_int(sen_entities):
    return int(sen_entities[0][len(SENT_PREFIX):])

def are_similar(gold_val, pred_val):
    if gold_val == pred_val:
        return True
    elif gold_val[-1] == '.' and gold_val[:-1].strip() == pred_val:
        return True
    elif pred_val[-1] == '.' and pred_val[:-1] == gold_val:
        return True
    else:
        return False
    #return (gold_val in pred_val) or (pred_val in gold_val)

def load(file):
    with open(file) as f:
        obj = pickle.load(f)
    return obj

def save(obj, file_name):
    with open(file_name, "w") as f:
        pickle.dump(obj, f)


def filter_duplicate_entities(merged_lists):
    dict = {(ent_tuple[0], ent_tuple[1][spacy_parser.ENT_OBJ_TEXT], ent_tuple[2][spacy_parser.ENT_OBJ_TEXT]):
                ent_tuple for ent_tuple in merged_lists}
    return list(dict.values())

def filter_ents(sen_entities_with_x, extracted_ents_rules):
    found_ents = set(extracted_ents_rules)
    filtered = []
    for ent_tuple in sen_entities_with_x:
        if (ent_tuple[0],ent_tuple[1], ent_tuple[2]) in found_ents:
            print("found ent in:" + str(ent_tuple[0]))
        else:
            filtered.append(ent_tuple)
    return filtered