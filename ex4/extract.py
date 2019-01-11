import sys

import numpy as np

import rules_extractor
import spacy_parser
import train
import utils
from Lexicon_helper import Lexicon_helper
from feature_extractor import FeatureExtractor
from utils import load


def print_results(pred_ents_list,data, out_path):
    with open(out_path, "w") as f:
        for pred_ents in pred_ents_list:
            sen_id = pred_ents[0]
            f.write("%s\t%s\t%s\t%s\t(%s)\n" % (sen_id,pred_ents[1], spacy_parser.LIVE_IN ,pred_ents[2], data[sen_id].text))


def filter_ent_pairs(predicted_entities_pairs, sen_entities_with_x):
    pairs=[]
    for i, p in enumerate(predicted_entities_pairs):
        if p == 1:
            tup = (sen_entities_with_x[i][0],sen_entities_with_x[i][1],sen_entities_with_x[i][2])
            pairs.append(tup)
    return pairs


def merge_lists(extracted_ent_paris_svm, extracted_ents_rules):
    full_list = set()
    for rules_ent_pairs in extracted_ents_rules:
        full_list.add(rules_ent_pairs)

    for ent_pair in extracted_ent_paris_svm:
        full_list.add(ent_pair)
    return full_list




if __name__ == '__main__':
    model_file = "model.pkl"
    features_file = "features.pkl"
    features_hasher_file = "features_hasher.pkl"

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    if "--model" in sys.argv:
        model_arg = sys.argv.index("--model")
        model_file = sys.argv[model_arg+1]
    if "--features" in sys.argv:
        features_arg = sys.argv.index("--features")
        features_file = sys.argv[features_arg+1]
    if "--feature_hasher" in sys.argv:
        feature_hasher_arg = sys.argv.index("--feature_hasher")
        features_hasher_file = sys.argv[feature_hasher_arg+1]

    clf = load(model_file)
    feature_set = load(features_file)
    feature_hasher = load(features_hasher_file)
    if train.check_file(input_file):
        print "file is in wrong format. expected raw and not proccessed file"

    data = {}
    for sen_id, sen in utils.read_lines(sys.argv[1]):
        data[sen_id] = utils.nlp(sen)

    lexicon_helper = Lexicon_helper()
    extracted_ent_paris_svm =[]
    feature_extractor = FeatureExtractor(lexicon_helper, feature_hasher, feature_set)
    sen_entities_with_x = spacy_parser.get_x_data(feature_extractor, data)
    sen_entities_with_x = sorted(sen_entities_with_x, key=utils.get_senid_int)
    allx = np.array([x[3].toarray()[0] for x in sen_entities_with_x])
    predicted_entities_pairs = clf.predict(allx)
    extracted_ent_paris_svm = filter_ent_pairs(predicted_entities_pairs, sen_entities_with_x)


    #Rules extraction
    extracted_ents_rules = rules_extractor.predict(data, lexicon_helper)
    extracted_ents_rules = sorted(extracted_ents_rules, key=utils.get_senid_int)

    all_extracted_ents = merge_lists(extracted_ent_paris_svm, extracted_ents_rules)

    print_results(all_extracted_ents, data, output_file)



