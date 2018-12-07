import sys
import ExtractFeatures_ner
import liblin
from ConvertFeatures import WORD_PREFIX, FEATURE_PREFIX, TAG_PREFIX

LINES_START = 0
LINES_LIMIT = float("inf")

id_to_tag = {}
tag_to_id = {}
id_to_feature = {}
feature_to_id = {}
predictor = None
popular_words = set()
popular_words_to_tags = {}
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

def is_tag_possible_for_word(word, tag):
    return word not in word_to_seen_tags or tag in word_to_seen_tags[word]

def predict_tags_for_line(line):
    v_dict = {}
    bp_dict = {}
    line_array = line.split()
    prediction_tags_array = [0] * len(line_array)
    max_values_for_normilazation = [0] * len(line_array)
    max_values_for_normilazation[0] = 1
    tag_set = set()
    old_2prevs_id = None
    old_prev_id = None
    old_scores = None
    for tag in tag_to_id.keys():
        tag_set.add(tag)
    tag_set.add('start')
    for i in range(len(line_array)):
        for possible_tag in tag_to_id.keys():
            if not is_tag_possible_for_word(line_array[i], possible_tag):
                continue
            first_prediction_for_tag = True
            for prev_tag in tag_set:
                if i < 1:
                    if prev_tag != 'start':
                        continue
                else:
                    if not is_tag_possible_for_word(line_array[i-1], prev_tag):
                        continue
                    if prev_tag == 'start':
                        continue
                # if prune_by_seq and (prev_tag, possible_tag) in impossible_seqs:
                #     continue
                max_viterbi_val = 0
                for prev_prev_tag in tag_set:
                    if i==0:
                        if prev_prev_tag == 'start' and prev_tag == 'start':
                            v_dict_val = 1
                        else:
                            continue
                    elif i == 1:
                        if prev_prev_tag != 'start':
                            continue
                    else:
                        if not is_tag_possible_for_word(line_array[i-2], prev_prev_tag):
                            continue
                        if prev_prev_tag == 'start':
                            continue
                        v_dict_val = v_dict[(i-1, prev_prev_tag, prev_tag)] if v_dict.has_key((i-1, prev_prev_tag, prev_tag)) else 0

                    if first_prediction_for_tag:
                        features_vec = get_features_vec(prev_prev_tag, prev_tag, line_array, i)
                        scored_tags_dict, old_scores = predictor.predict(features_vec)
                        first_prediction_for_tag = False
                    else:
                        new_prev_id = feature_to_id.get(ExtractFeatures_ner.get_feat_str_by_prevtag(prev_tag), None)
                        new_2prevs_id = feature_to_id\
                            .get(ExtractFeatures_ner.get_feat_str_by_2prevs(prev_prev_tag, prev_tag), None)
                        scored_tags_dict, old_scores = predictor.predict_with_trasitions_change(old_scores, old_prev_id,
                                                                                    old_2prevs_id, new_prev_id,
                                                                                    new_2prevs_id)

                    old_prev_id = feature_to_id.get(ExtractFeatures_ner.get_feat_str_by_prevtag(prev_tag), None)
                    old_2prevs_id = feature_to_id.get(ExtractFeatures_ner
                                                      .get_feat_str_by_2prevs(prev_prev_tag, prev_tag), None)
                    # print ("scored_tags_dict" + repr(scored_tags_dict))
                    # print ("old_scores" + repr(old_scores))

                    # print("i= %d" % i)
                    # print(possible_tag)
                    # print (tag_to_id[possible_tag])
                    # print(scored_tags_dict[tag_to_id[possible_tag]])
                    # print("n=%f" % max_values_for_normilazation[i])
                    viterbi_val = (v_dict_val / float(max_values_for_normilazation[i])) * \
                              scored_tags_dict[tag_to_id[possible_tag]]

                    if viterbi_val > max_viterbi_val:
                        # print("v=%f max=%f" % (viterbi_val, max_viterbi_val))
                        if i < len(line_array)-1 and viterbi_val > max_values_for_normilazation[i+1]:
                            max_values_for_normilazation[i+1] = viterbi_val
                        max_viterbi_val = viterbi_val
                        v_dict[(i, prev_tag, possible_tag)] = viterbi_val
                        bp_dict[(i, prev_tag, possible_tag)] = prev_prev_tag

    #prediction_tags_array[len(line_array)-1]
    max_viterbi_val = 0
    for possible_tag in tag_to_id.keys():
        for prev_tag in tag_set:
            v_dict_val = v_dict[(len(line_array)-1, prev_tag, possible_tag)] \
                if v_dict.has_key((len(line_array)-1, prev_tag, possible_tag)) else 0
            if v_dict_val > max_viterbi_val:
                max_viterbi_val = v_dict_val
                prediction_tags_array[len(line_array)-1] = possible_tag
    #prediction_tags_array[len(line_array)-2]
    max_viterbi_val = 0
    for possible_tag in tag_to_id.keys():
        for prev_tag in tag_set:
            v_dict_val = v_dict[(len(line_array)-2, prev_tag, possible_tag)] if \
                v_dict.has_key((len(line_array)-2, prev_tag, possible_tag)) else 0
            if v_dict_val > max_viterbi_val:
                max_viterbi_val = v_dict_val
                prediction_tags_array[len(line_array)-2] = possible_tag

    for i in range(len(line_array)-3, -1, -1):
        prediction_tags_array[i] = bp_dict[(i+2, prediction_tags_array[i+1], prediction_tags_array[i+2])]

    return prediction_tags_array


def predict_viterbi(file_name):
    all_tags_predictions = []
    original_lines = []
    with open(file_name) as f:
        content = f.readlines()
        line_num = 0
        for line in content:
            line_num += 1
            if line_num < LINES_START:
                continue
            if line_num > LINES_LIMIT:
                break

            tags_arr = predict_tags_for_line(line)
            # except:
            #     global prune_by_seq
            #     print ("dropped prune by seq at line number "+repr(line_num))
            #     prune_by_seq = False
            #     tags_arr = predict_tags_for_line(line)

            all_tags_predictions.append(tags_arr)
            original_lines.append(line.split())
            print "predicted line %d" % line_num

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
    feature_str += ExtractFeatures_ner.get_features_by_word(line_array[word_index], is_rare)
    feature_str += ExtractFeatures_ner.get_features_by_2_prevs(prev_prev_arr, prev_arr)
    feature_str += ExtractFeatures_ner.get_features_by_next_word(next_arr)
    feature_str += ExtractFeatures_ner.get_features_by_next_next_word(next_next_arr)
    feature_str += ExtractFeatures_ner.get_features_by_lexicons(line_array[word_index], line_array, word_index)
    return feature_str

if __name__ == '__main__':
    input_file_name = sys.argv[1]
    model_name = sys.argv[2]
    feature_map_file = sys.argv[3]
    out_file_name = sys.argv[4]
    lexicon_dir = sys.argv[5]

    ExtractFeatures_ner.load_lexicons(lexicon_dir)
    predictor = liblin.LiblinearLogregPredictor(model_name)
    load_feature_map(feature_map_file)
    predictions,original_lines = predict_viterbi(input_file_name)
    print_output(out_file_name, original_lines, predictions)

