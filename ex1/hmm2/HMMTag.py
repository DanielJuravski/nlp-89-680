import numpy as np# This Script is responsible for loading and calcualting q.mle and e.mle
import sys

LINES_START = 1
LINES_LIMIT = float('inf')


singles_dict = {} #indexed by the tag, value is the amount
doubles_dict_by_prev = {} #indexed by the prvious tag, value is dictionary of tag and amount
triples_dict_by_secondprev_and_prev = {} #indexed by a tuple of (second_prev, prev), , value is dictionary of tag and amount
e_dict = {}
num_of_words = 0 #count all words, not distinct
gamma1 = 0.7
gamma2 = 0.2
gamma3 =0.1
sum_words_int_test_file = 0
unkowns_in_test_file = 0
v_dict = {}
bp_dict = {}
impossible_seqs = set()
prune_by_seq = True


def add_to_singles(tags_arr):
    tag = tags_arr[0]
    amount = tags_arr[1]
    if singles_dict.has_key(tag):
        singles_dict[tag] += int(amount)
    else:
        singles_dict[tag] = int(amount)


def add_to_doubles(tags_arr):
    prev_tag = tags_arr[0]
    curr_tag = tags_arr[1]
    amount = tags_arr[2]
    if doubles_dict_by_prev.has_key(prev_tag):
        tag_dict = doubles_dict_by_prev[prev_tag]
    else:
        tag_dict = {}

    if tag_dict.has_key(curr_tag):
        tag_dict[curr_tag] += int(amount)
    else:
        tag_dict[curr_tag] = int(amount)

    doubles_dict_by_prev[prev_tag] = tag_dict


def add_to_triples(tags_arr):
    second_prev_tag = tags_arr[0]
    prev_tag = tags_arr[1]
    curr_tag = tags_arr[2]
    amount = tags_arr[3]
    key=(second_prev_tag,prev_tag)
    if triples_dict_by_secondprev_and_prev.has_key(key):
        tag_dict = triples_dict_by_secondprev_and_prev[key]
    else:
        tag_dict = {}

    if tag_dict.has_key(curr_tag):
        tag_dict[curr_tag] += int(amount)
    else:
        tag_dict[curr_tag] = int(amount)

    triples_dict_by_secondprev_and_prev[key] = tag_dict


def load_q_mle(file_name):
    with open(file_name) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        for line in content:
            tags_arr = line.split()
            if len(tags_arr) == 2:
                add_to_singles(tags_arr)
            elif len(tags_arr) == 3:
                add_to_doubles(tags_arr)
            elif len(tags_arr) == 4:
                add_to_triples(tags_arr)
            else:
                print "error unknown number of spaces in q.mle for line " + repr(tags_arr)


def load_e_mle(file_name):
    with open(file_name) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        for line in content:
            arr = line.split()
            word = arr[0]
            tag = arr[1]
            amount = arr[2]
            if e_dict.has_key(word):
                tag_dict = e_dict[word]
            else:
                tag_dict = {}

            tag_dict[tag] = int(amount)
            e_dict[word] = tag_dict
            global num_of_words
            num_of_words += int(amount)

def load_extra_args(file_name):
    if not file_name:
        return

    with open(file_name) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        for line in content:
            arr = line.split()
            if len(arr) == 2:
                impossible_seqs.add((arr[0],arr[1]))
            elif len(arr) == 3:
                impossible_seqs.add((arr[0],arr[1],arr[2]))
            else:
                continue

def get_q_estimation(second_prev_tag, prev_tag, tag):
    # count(a,b,c)
    countABC = 0.0
    if triples_dict_by_secondprev_and_prev.has_key((second_prev_tag, prev_tag)):
        if triples_dict_by_secondprev_and_prev[(second_prev_tag, prev_tag)].get(tag, 0):
            countABC = float(triples_dict_by_secondprev_and_prev[(second_prev_tag, prev_tag)].get(tag, 0))

    countAB = 1.0
    # count(a,b) - denominator
    if doubles_dict_by_prev.has_key(second_prev_tag):
        if doubles_dict_by_prev[second_prev_tag].get(prev_tag, 0):
            countAB = float(doubles_dict_by_prev[second_prev_tag].get(prev_tag, 0))


    # count(b,c)
    if doubles_dict_by_prev.has_key(prev_tag):
        countBC = float(doubles_dict_by_prev[prev_tag].get(tag, 0))
    else:
        countBC = 0.0

    # count(b)
    if singles_dict.has_key(prev_tag):
        countB = float(singles_dict[prev_tag])
    else:
        countB = 1.0

    # count(c)
    if singles_dict.has_key(tag):
        countC = float(singles_dict[tag])
    else:
        countC = 0.0
    q_estimate = gamma1 * (countABC / countAB) + gamma2 * (countBC / countB) + gamma3 * (countC / num_of_words)

    return q_estimate


def get_e_estimation(word, tag, word_index):
    if word not in e_dict:
        e_estimate_patterns = find_tag_for_unk(word, tag, word_index)
        e_estimate = (0 if tag not in e_dict['unk'] else float(e_dict['unk'][tag])) / float(singles_dict[tag])
        if e_estimate < e_estimate_patterns:
            e_estimate = e_estimate_patterns
    else:
        e_estimate = (0 if tag not in e_dict[word] else float(e_dict[word][tag])) / float(singles_dict[tag])

    return e_estimate

def find_tag_for_unk(word, tag, word_index):
    score = 0

    # numeric case:
    if tag == 'CD':
        def isfloat(value):
            try:
                tofloat = float(value.replace(',', ''))
                return True
            except ValueError:
                return False
        def istime(value):
            arr = value.split(':')
            for i in range(len(arr)):
                if not isfloat(arr[i]):
                    return False
                return True
        def isScore(value):
            arr = value.split('-')
            for i in range(len(arr)):
                if not isfloat(arr[i]):
                    return False
            return True

        if isfloat(word) or istime(word) or isScore(word):
            score = 1

    elif word.endswith('ing'):
        score = (float(e_dict['^_ing'].get(tag,0))) / float(singles_dict[tag])

    elif word.endswith('ed'):
        score = (float(e_dict['^_ed'].get(tag,0))) / float(singles_dict[tag])

    elif word.endswith('s'):
        score = (float(e_dict['^_s'].get(tag,0))) / float(singles_dict[tag])

    if word[0].isupper() and word_index != 0 and not word.isupper():
        score = (float(e_dict['^A_'].get(tag))) / float(singles_dict[tag])
    elif word.isalpha() and word.isupper():
        score = (float(e_dict['^ABC'].get(tag,0))) / float(singles_dict[tag])

    return score

def is_tag_possible_for_word(word, possible_tag):
    if word not in e_dict:
        return True
    elif possible_tag not in e_dict[word]:
        return False
    else:
        return True


def predict_tags_for_line(line):
    v_dict = {}
    bp_dict = {}
    line_array = line.split()
    prediction_tags_array = [0] * len(line_array)
    max_values_for_normilazation = [0] * len(line_array)
    max_values_for_normilazation[0] = 1
    for i in range(len(line_array)):
        for possible_tag in singles_dict.keys():
            if possible_tag == 'start':
                continue
            if not is_tag_possible_for_word(line_array[i], possible_tag):
                continue
            for prev_tag in singles_dict.keys():
                max_viterbi_val = 0
                if i < 1:
                    if prev_tag != 'start':
                        continue
                else:
                    if not is_tag_possible_for_word(line_array[i-1], prev_tag):
                        continue
                if prune_by_seq and (prev_tag, possible_tag) in impossible_seqs:
                    continue
                for prev_prev_tag in singles_dict.keys():
                    if i == 0:
                        if prev_prev_tag == 'start' and prev_tag == 'start':
                            v_dict_val = 1
                        else:
                            continue
                    else:
                        if i < 2:
                            if prev_prev_tag != 'start':
                                continue
                        else:
                            if not is_tag_possible_for_word(line_array[i-2], prev_prev_tag):
                                continue
                        v_dict_val = v_dict[(i-1, prev_prev_tag, prev_tag)] if v_dict.has_key((i-1, prev_prev_tag, prev_tag)) else 0
                    viterbi_val = (v_dict_val / float(max_values_for_normilazation[i])) *\
                                  (get_q_estimation(prev_prev_tag, prev_tag, possible_tag)) * \
                            (get_e_estimation(line_array[i], possible_tag, i))

                    if viterbi_val > max_viterbi_val:
                        if i < len(line_array)-1 and viterbi_val > max_values_for_normilazation[i+1] :
                            max_values_for_normilazation[i+1] = viterbi_val
                        max_viterbi_val = viterbi_val
                        v_dict[(i, prev_tag, possible_tag)] = viterbi_val
                        bp_dict[(i, prev_tag, possible_tag)] = prev_prev_tag

    #prediction_tags_array[len(line_array)-1]
    max_viterbi_val = 0
    for possible_tag in singles_dict.keys():
        for prev_tag in singles_dict.keys():
                v_dict_val = v_dict[(len(line_array)-1, prev_tag, possible_tag)] \
                    if v_dict.has_key((len(line_array)-1, prev_tag, possible_tag)) else 0
                if v_dict_val > max_viterbi_val:
                    max_viterbi_val = v_dict_val
                    prediction_tags_array[len(line_array)-1] = possible_tag
    #prediction_tags_array[len(line_array)-2]
    max_viterbi_val = 0
    for possible_tag in singles_dict.keys():
        for prev_tag in singles_dict.keys():
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

            try:
                tags_arr = predict_tags_for_line(line)
            except:
                global prune_by_seq
                print ("dropped prune by seq at line number "+repr(line_num))
                prune_by_seq = False
                tags_arr = predict_tags_for_line(line)

            all_tags_predictions.append(tags_arr)
            original_lines.append(line.split())
            print "predicted line %d" % line_num

    return all_tags_predictions, original_lines


def compare_predictions_to_answers(prediction_tags_arr, answers_file):
    with open(answers_file) as f:
        content=f.readlines()
        content=[x.strip() for x in content]
        i = 0
        bad_results = 0
        good_results = 0
        line_num = 0
        for line in content:
            line_num += 1
            if line_num < LINES_START:
                continue
            if line_num > LINES_LIMIT:
                break
            prediction_tags_for_line = prediction_tags_arr[i]
            answer_pairs = line.split()
            for j in range(len(answer_pairs)):
                answer_tag = answer_pairs[j].split("/")[1]
                if answer_tag == prediction_tags_for_line[j]:
                    good_results += 1
                else:
                    bad_results += 1
            i += 1

        return (good_results, bad_results)


def append_missing_unk_tags_with_1():
    for tag in singles_dict:
        if tag not in e_dict['unk']:
            e_dict['unk'][tag] = 1

def append_missing_ing_tags_with_1():
    for tag in singles_dict:
        if tag not in e_dict['^_ing']:
            e_dict['^_ing'][tag] = 1


def append_missing_ed_tags_with_1():
    for tag in singles_dict:
        if tag not in e_dict['^_ed']:
            e_dict['^_ed'][tag] = 1


def append_missing_UC_tags_with_1():
    for tag in singles_dict:
        if tag not in e_dict['^A_']:
            e_dict['^A_'][tag] = 1

def print_output(out_file_name, original_lines, predictions):
    output = open(out_file_name, 'w')
    for i in range(len(original_lines)):
        line = original_lines[i]
        tags = predictions[i]
        for j in range(len(line)):
            output.write("%s/%s " % (line[j], tags[j]))
        output.writelines("\n")
    output.close()

if __name__ == '__main__':

    input_file_name = sys.argv[1]
    q_mle_filename = sys.argv[2]
    e_mle_filename = sys.argv[3]
    out_file_name = sys.argv[4]

    if len(sys.argv) > 5:
        extra_file_name = sys.argv[5]
        load_extra_args(extra_file_name)

    load_q_mle(q_mle_filename)
    load_e_mle(e_mle_filename)


    append_missing_unk_tags_with_1()
    append_missing_ing_tags_with_1()
    append_missing_ed_tags_with_1()
    append_missing_UC_tags_with_1()

    (predictions, original_lines) = predict_viterbi(input_file_name)
    print_output(out_file_name, original_lines, predictions)