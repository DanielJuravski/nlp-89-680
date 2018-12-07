import sys
import ExtractFeatures
import liblin
from ConvertFeatures import WORD_PREFIX, FEATURE_PREFIX, TAG_PREFIX

LINES_START = 1
LINES_LIMIT = float("inf")

id_to_tag = {}
tag_to_id = {}
id_to_feature = {}
feature_to_id = {}
predictor = None
popular_words = set()
word_to_seen_tags = {}


def is_tag_line(line):
    return line[:len(TAG_PREFIX)] == TAG_PREFIX


def add_tag_to_dicts(line):
    line = line[len(TAG_PREFIX):]
    arr = line.split()
    tag = arr[0]
    id = arr[1]
    tag_to_id[tag] = id
    id_to_tag[id] = tag


def add_feature_to_dicts(line):
    line = line[len(FEATURE_PREFIX):]
    arr = line.split()
    feature = arr[0]
    id = int(arr[1])
    feature_to_id[feature] = id
    id_to_feature[id] = feature
    if "form=" == feature[:5]:
        popular_words.add(feature[5:])


def add_word_to_dict(line):
    line = line[len(WORD_PREFIX):]
    arr = line.split()
    word = arr[0]
    tag = arr[1]
    if word not in word_to_seen_tags:
        word_to_seen_tags[word] = set()
    word_to_seen_tags[word].add(tag)


def is_word_line(line):
    return line[:len(WORD_PREFIX)] == WORD_PREFIX


def load_feature_map(feature_map_file):
    with open(feature_map_file) as f:
        content = f.readlines()

    content=[x.strip() for x in content]
    for line in content:
        if is_tag_line(line):
            add_tag_to_dicts(line)
        elif is_word_line(line):
            add_word_to_dict(line)
        else:
            add_feature_to_dicts(line)


def get_features_vec(second_prev, prev, line_array, word_index):
    features_str_arr = get_features_str(second_prev, prev, line_array, word_index).split()
    features_ids_arr = []
    for str in features_str_arr:
        if str in feature_to_id:
            features_ids_arr.append(feature_to_id[str])
    features_ids_arr.sort()
    return features_ids_arr


def predict_tag(second_prev, prev, line_array, word_index):
    features_vec = get_features_vec(second_prev, prev, line_array, word_index)
    max = 0
    prediction_tag = None

    scored_tags_dict, raw_scores = predictor.predict(features_vec)
    for tag_id in id_to_tag:
        if scored_tags_dict[tag_id] > max:
            max = scored_tags_dict[tag_id]
            prediction_tag = id_to_tag[tag_id]

    return prediction_tag


def predict_tags_for_line(line):
    line_array = line.split()
    prediction_tags_array = [None] * len(line_array)
    for i in range(len(line_array)):
        if i == 0:
            second_prev = 'start'
            prev = 'start'
        elif i == 1:
            second_prev = 'start'
            prev = prediction_tags_array[i-1]
        else:
            second_prev = prediction_tags_array[i-2]
            prev = prediction_tags_array[i-1]

        prediction_tags_array[i] = predict_tag(second_prev, prev, line_array, i)
    return prediction_tags_array


def predict_greedy(file_name):
    all_tags_predictions = []
    original_lines = []
    with open(file_name) as f:
        content = f.readlines()
        line_num = 0
        for line in content:
            line_num += 1
            if line_num < LINES_START or line_num > LINES_LIMIT:
                continue

            print("predicting line %d" % line_num)
            original_lines.append(line.split())
            tags_arr = predict_tags_for_line(line)
            all_tags_predictions.append(tags_arr)

    return all_tags_predictions, original_lines


def print_output(out_file_name, original_lines, predictions):
    output = open(out_file_name, 'w')
    for i in range(len(original_lines)):
        line = original_lines[i]
        tags = predictions[i]
        for j in range(len(line)):
            output.write("%s/%s " % (line[j], tags[j]))
        output.writelines("\n")
    output.close()


def get_features_str(prev_prev_tag, prev_tag, line_array, word_index):
    if word_index < 1:
        prev_arr = [None, prev_tag]
        prev_prev_arr = [None, prev_prev_tag]
    elif word_index < 2:
        prev_arr = [line_array[word_index-1], prev_tag]
        prev_prev_arr = [None, prev_prev_tag]
    else:
        prev_arr = [line_array[word_index-1], prev_tag]
        prev_prev_arr = [line_array[word_index-2], prev_prev_tag]

    if word_index > (len(line_array)-2):
        next_arr = [None, None]
        next_next_arr = [None, None]
    elif word_index > (len(line_array)-3):
        next_arr = [line_array[word_index+1], None]
        next_next_arr = [None, None]
    else:
        next_arr = [line_array[word_index+1], None]
        next_next_arr = [line_array[word_index+2], None]
    is_rare = line_array[word_index] not in popular_words
    feature_str = ""
    feature_str += ExtractFeatures.get_features_by_word(line_array[word_index], is_rare)
    feature_str += ExtractFeatures.get_features_by_2_prevs(prev_prev_arr, prev_arr)
    feature_str += ExtractFeatures.get_features_by_next_word(next_arr)
    feature_str += ExtractFeatures.get_features_by_next_next_word(next_next_arr)
    return feature_str

if __name__ == '__main__':
    input_file_name = sys.argv[1]
    model_name = sys.argv[2]
    feature_map_file = sys.argv[3]
    out_file_name = sys.argv[4]

    predictor = liblin.LiblinearLogregPredictor(model_name)
    load_feature_map(feature_map_file)
    predictions,original_lines = predict_greedy(input_file_name)
    print_output(out_file_name, original_lines, predictions)

