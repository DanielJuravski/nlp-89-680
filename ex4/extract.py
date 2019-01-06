import pickle
import sys

import spacy_parser
import train2
from feature_extractor import FeatureExtractor
import numpy as np
import utils
from utils import load


def print_results(pred_ents, sen_entities_with_x,raw_sentences, out_path):
    with open(out_path, "w") as f:
        for i, p in enumerate(pred_ents):
            if p == 1:
                sen_ents_data = sen_entities_with_x[i]
                sen_id = sen_ents_data[0]
                f.write("%s\t%s\t%s\t%s\t%s\n" % (sen_id,sen_ents_data[1], spacy_parser.LIVE_IN ,sen_ents_data[2], data[sen_id].text))


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
    if train2.check_file(input_file):
        print "file is in wrong format. expected raw and not proccessed file"

    data = {}
    for sen_id, sen in utils.read_lines(sys.argv[1]):
        data[sen_id] = utils.nlp(sen)

    feature_extractor = FeatureExtractor(feature_hasher, feature_set)
    sen_entities_with_x = spacy_parser.get_x_data(feature_extractor, data)
    sen_entities_with_x = sorted(sen_entities_with_x, key=utils.get_senid_int)
    allx = np.array([x[3].toarray()[0] for x in sen_entities_with_x])
    predicted_entities_pairs = clf.predict(allx)
    print_results(predicted_entities_pairs, sen_entities_with_x, data, output_file)

