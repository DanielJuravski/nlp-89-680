import pickle
import sys
import train
from feature_extractor import FeatureExtractor
import numpy as np
from utils import load

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
    if not train.check_file(input_file):
        print "file is in wrong format. expected proccessed file"

    feature_extractor = FeatureExtractor(feature_hasher, feature_set)
    sentences = train.load_processed_sentences(input_file)
    sen_entities_with_x = train.get_x_data(feature_extractor, sentences)
    allx = np.array([x[3].toarray()[0] for x in sen_entities_with_x])
    train_pred = clf.predict(allx)
    counter = 0
    for i,p in enumerate(train_pred):
        if p==1:
            print (str(counter) +": "+ str(sen_entities_with_x[i][:3]))
            counter += 1

