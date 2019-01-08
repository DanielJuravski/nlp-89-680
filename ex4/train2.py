import sys

import numpy as np
from sklearn.svm import LinearSVC
from Lexicon_helper import Lexicon_helper
import utils
from feature_extractor import FeatureExtractor
from spacy_parser import get_x_data, LIVE_IN, ENT_OBJ_TEXT
from utils import save

GOLD_ENT2 = 2
GOLD_RELATION = 1
GOLD_ENT1 = 0
ENTITY_COUPLE_OBJ_ENT2 = 2
ENTITY_COUPLE_OBJ_ENT1 = 1
ENTITIY_COUPLE_OBJ_SENID = 0

def check_file(input_file):
    with open(input_file) as f:
        content = f.readlines()
        if content[0][0] != '#':
            return False
        else:
            return True


def load_annotation_sentences(annotations_file):
    all_annotated_sentences = {}
    with open(annotations_file) as f:
        content = f.readlines()
        for line in content:
            line_arr = line.split("\t")
            sent_id = line_arr[0]
            sents_arr = all_annotated_sentences.get(sent_id, [])
            sents_arr.append((line_arr[1], line_arr[2], line_arr[3]))
            all_annotated_sentences[sent_id] = sents_arr

    return all_annotated_sentences


def comapre_to_gold_lines(ent1, ent2, gold_lines):
    for line in gold_lines:
        if line[GOLD_RELATION] == LIVE_IN:
            if utils.are_similar(ent1, line[GOLD_ENT1]) and utils.are_similar(ent2, line[GOLD_ENT2]):
                return True
    return False


def output_pos_ents_for_debug(pos_entities):
    with open("debug_pos_ents.txt", "w") as f:
        for ent in pos_entities:
            f.write(repr(ent))


def tag_entities(sen_entities_with_x, annotation_sentences):
    pos_entities = []
    tagged_sen_entites = []
    for entitys_couple_object in sen_entities_with_x:
        sen_id = entitys_couple_object[ENTITIY_COUPLE_OBJ_SENID]
        gold_lines = annotation_sentences[sen_id]
        if comapre_to_gold_lines(entitys_couple_object[ENTITY_COUPLE_OBJ_ENT1],
                                 entitys_couple_object[ENTITY_COUPLE_OBJ_ENT2],
                                 gold_lines):
            tagged_sen_entites.append(entitys_couple_object+(1,))
            pos_entities.append(entitys_couple_object)
        else:
            tagged_sen_entites.append(entitys_couple_object+(0,))

    output_pos_ents_for_debug(pos_entities)
    return tagged_sen_entites


if __name__ == '__main__':
    model_file = "model.pkl"
    raw_file = sys.argv[1]
    annotations_file = sys.argv[2]
    if check_file(raw_file):
        print "file is in wrong format expected raw and not proccessed file"

    data = {}
    for sen_id, sen in utils.read_lines(sys.argv[1]):
        data[sen_id] = utils.nlp(sen)

    annotation_sentences = load_annotation_sentences(annotations_file)
    lexicon_helper = Lexicon_helper()
    feature_extractor = FeatureExtractor(lexicon_helper)
    sen_entities_with_x = get_x_data(feature_extractor, data)
    tagged_sen_entites = tag_entities(sen_entities_with_x, annotation_sentences)
    clf = LinearSVC(random_state=0, tol=1e-5)
    allx = np.array([x[3].toarray()[0] for x in tagged_sen_entites])
    yall = np.array([y[4] for y in tagged_sen_entites])
    clf.fit(allx, yall)

    save(clf, model_file)
    save(feature_extractor.features_set, "features.pkl")
    save(feature_extractor.feature_hasher, "features_hasher.pkl")

