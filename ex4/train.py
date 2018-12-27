import sys

import numpy as np
from sklearn.svm import LinearSVC

import utils
from feature_extractor import FeatureExtractor
from utils import save

LIVE_IN = "Live_In"

GOLD_ENT2 = 2

GOLD_RELATION = 1

GOLD_ENT1 = 0

ENTITY_OBJ_ENT2 = 2

ENTITY_OBJ_ENT1 = 1

ENTITIY_OBJ_SENID = 0

PROCESSED_LINE_NER_BIO = 7

ID_LINE_PREF = "#id: "


def check_file(input_file):
    with open(input_file) as f:
        content = f.readlines()
        if content[0][0] != '#':
            return False
        else:
            return True


def load_processed_sentences(processed_file):
    all_sentences = {}
    with open(processed_file) as f:
        content = f.readlines()
        sent_id = ""
        for line in content:
            line_arr = line.split()
            if not line_arr:
                continue
            elif line[:len(ID_LINE_PREF)] == ID_LINE_PREF:
                sent_id = line[len(ID_LINE_PREF):].strip()
                all_sentences[sent_id] = []
            else:
                all_sentences[sent_id].append(line_arr)

    return all_sentences


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



def get_xs_from_sen(sen_id, sentence):
    """

    :param sen_id:
    :param sentence:
    :return array of tuples (sen_id, ent1, ent2):
    """
    xs = []
    entities = []
    curr_entity = []
    for line in sentence:
        if "#text:" in line[0]:
            continue
        if line[PROCESSED_LINE_NER_BIO] == 'B' and len(curr_entity) > 0:
            entities.append(curr_entity)
            curr_entity = []
        elif line[PROCESSED_LINE_NER_BIO] != 'O':
           curr_entity.append(line)
        else:
            if len(curr_entity) > 0:
                entities.append(curr_entity)
                curr_entity = []

    if len(curr_entity) > 0:
        entities.append(curr_entity)

    for i, ent_i in enumerate(entities):
        for j, ent_j in enumerate(entities):
            if i != j:
                xs.append((sen_id, ent_i, ent_j))

    return xs

def get_x_data(feature_extractor, processed_sentences):
    all_x_ent_tuples_data = []
    for sen_id in processed_sentences:
        sentence_x_data = get_xs_from_sen(sen_id,processed_sentences[sen_id])
        all_x_ent_tuples_data += sentence_x_data

    all_x_data = []
    for ent_tuple in all_x_ent_tuples_data:
        extracted_x = feature_extractor.extract_features(ent_tuple, processed_sentences[ent_tuple[0]])
        all_x_data.append(extracted_x)

    sen_entities, x_data = feature_extractor.build_x_vectors(all_x_data)
    return sen_entities


def comapre_to_gold_lines(ent1, ent2, gold_lines):
    for line in gold_lines:
        if line[GOLD_RELATION] == LIVE_IN:
            if utils.are_similar(ent1, line[GOLD_ENT1]) and utils.are_similar(ent2, line[GOLD_ENT2]):
                return True
    return False


def tag_entities(sen_entities_with_x, annotation_sentences):
    tagged_sen_entites = []
    for entitys_object in sen_entities_with_x:
        sen_id = entitys_object[ENTITIY_OBJ_SENID]
        gold_lines = annotation_sentences[sen_id]
        if comapre_to_gold_lines(entitys_object[ENTITY_OBJ_ENT1], entitys_object[ENTITY_OBJ_ENT2], gold_lines):
            tagged_sen_entites.append(entitys_object+(1,))
        else:
            tagged_sen_entites.append(entitys_object+(0,))
    return tagged_sen_entites


if __name__ == '__main__':
    model_file = "model.pkl"
    processed_file = sys.argv[1]
    annotations_file = sys.argv[2]
    if not check_file(processed_file):
        print "file is in wrong format expected proccessed file"

    processed_sentences = load_processed_sentences(processed_file)
    annotation_sentences = load_annotation_sentences(annotations_file)
    feature_extractor = FeatureExtractor()
    sen_entities_with_x = get_x_data(feature_extractor, processed_sentences)
    tagged_sen_entites = tag_entities(sen_entities_with_x, annotation_sentences)
    clf = LinearSVC(random_state=0, tol=1e-5)
    allx = np.array([x[3].toarray()[0] for x in tagged_sen_entites])
    yall = np.array([y[4] for y in tagged_sen_entites])
    clf.fit(allx, yall)

    save(clf, model_file)
    save(feature_extractor.features_set, "features.pkl")
    save(feature_extractor.feature_hasher, "features_hasher.pkl")







