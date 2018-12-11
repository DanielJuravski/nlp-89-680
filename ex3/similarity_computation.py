import sys
from collections import Counter

import datetime
import numpy as np
import operator
from close_words import print_tables

TARGET_WORDS = ["car", "bus", "hospital", "hotel", "gun", "bomb", "horse", "fox", "table", "bowl", "guitar", "piano"]

p_word_dict = {}
p_att_dict = {}
p_word_att_dict = {}

SMOOTHING_FACTOR = 1

def safe_div(x,y):
    if y == 0:
        return 0
    return x / float(y)


def PMI(u_att_count, u_att_total_count, u_count, u_total_count, att_count, att_total_count):

    p_u_att = safe_div(u_att_count**SMOOTHING_FACTOR, u_att_total_count)
    p_u = safe_div(u_count**SMOOTHING_FACTOR, u_total_count)
    p_att = safe_div(att_count**SMOOTHING_FACTOR, att_total_count)

    cond_pmi = safe_div(p_u_att, (p_u*p_att))
    cond_pmi = np.log(cond_pmi)

    pmi = np.max((0, cond_pmi))

    return pmi, p_u_att, p_u, p_att

#loads the words that passed a threshold
def get_valid_words(good_words_file):
    good_dict = Counter()
    with open(good_words_file) as f:
        for line in f.readlines():
            word, count = line.split()
            good_dict[word] = int(count)

    return good_dict


def loadData(data_file_name, good_words_file):
    """
    parse file to main dict where the key is WORD and the value is dict of {where the key is context word and the value is the count}
    :param data_file_name:
    :return: main_dict
    """
    main_dict = Counter()
    attribute_dict = Counter()

    total_word_occurrence_count = Counter()
    total_context_occurrence_count = Counter()

    good_words_dict = get_valid_words(good_words_file)

    # create main_dict with count values
    with open(data_file_name) as f:
        print "Creating main_dict ..."
        for line in f.readlines():
            curr_word, curr_context, word_context_count = line.split()
            word_context_count = int(word_context_count)

            if curr_word in good_words_dict:
                if curr_word not in main_dict:
                    main_dict[curr_word] = Counter()
                main_dict[curr_word][curr_context] = word_context_count
                total_word_occurrence_count[curr_word] = good_words_dict[curr_word]
                total_context_occurrence_count[curr_context] += word_context_count
                if curr_context in attribute_dict:
                    attribute_dict[curr_context].add(curr_word)
                else:
                    context_set = set()
                    context_set.add(curr_word)
                    attribute_dict[curr_context] = context_set

    print ('Number of words in main_dict: ' + str(len(main_dict)))

    # set PMI values for the main_dict
    print "Setting PMI values ..."

    def smooth(arr):
        return [i**SMOOTHING_FACTOR for i in arr]

    total_words_count = sum(smooth(total_word_occurrence_count.values()))
    total_context_count = sum(smooth(total_context_occurrence_count.values()))
    total_word_context_count = sum([sum(smooth(main_dict[x].values())) for x in main_dict])

    for word in main_dict:
        total_PMI = 0
        all_word_context = main_dict[word]
        for word_context in all_word_context:
            word_context_occurrence = all_word_context[word_context]
            word_count = total_word_occurrence_count[word]
            context_count = total_context_occurrence_count[word_context]

            word_context_PMI, p_u_att, p_u, p_att = PMI(word_context_occurrence, total_word_context_count,
                                    word_count, total_words_count,
                                    context_count, total_context_count)

            total_PMI += word_context_PMI ** 2

            all_word_context[word_context] = word_context_PMI

            p_word_dict[word] = p_u
            p_att_dict[word_context] = p_att
            p_word_att_dict[(word, word_context)] = p_u_att
        total_PMI = np.sqrt(total_PMI)
        for word_context in all_word_context:
            all_word_context[word_context] = (all_word_context[word_context] / float(total_PMI)) if float(total_PMI) > 0 else 0


    print sum(p_word_dict.values())
    print sum(p_att_dict.values())
    print sum(p_word_att_dict.values())

    return main_dict, attribute_dict


def findSimilar(u, main_dict, attribute_dict, num_of_words):
    if u in main_dict:
        print "Word '" + u + "' found in main_dict ..."
        DT = Counter()

        u_attributes = main_dict[u]
        for att in u_attributes:
            for word in attribute_dict[att]:
                word_attributes = main_dict[word]
                if att in word_attributes:
                    DT[word] += u_attributes[att] * word_attributes[att]

        sorted_DT = sorted(DT.items(), key=operator.itemgetter(1), reverse=True)
        final_words = sorted_DT[:num_of_words]
        return [x[0] for x in final_words]

    else:
        print "ERROR: no word '" + u + "' in main_dict !"


def find_highest_contexts(target_word, main_dict, max_attributes):
    if target_word in main_dict:
        print "Word '" + target_word + "' found in main_dict ..."
        target_word_attributes = main_dict[target_word]
        sorted_attributes = sorted(target_word_attributes.items(), key=operator.itemgetter(1), reverse=True)
        return [x[0] for x in sorted_attributes[:max_attributes]]


def init_global_dicts():
    global p_word_dict, p_att_dict,p_word_att_dict
    p_word_dict = {}
    p_att_dict = {}
    p_word_att_dict = {}


def get_similarities(data_file_name, valid_words_file):
    main_dict, attribute_dict = loadData(data_file_name, valid_words_file)
    similar_words_dict = {}
    strongest_context_dict = {}
    for target_word in TARGET_WORDS:
        similar_words = findSimilar(target_word, main_dict, attribute_dict, 21)
        similar_words = similar_words[1:] #remove first word
        similar_words_dict[target_word] = similar_words

        highest_contexts = find_highest_contexts(target_word, main_dict, 21)
        strongest_context_dict[target_word] = highest_contexts

    return similar_words_dict, strongest_context_dict

if __name__ == '__main__':
    num_of_tasks = int(sys.argv[1])
    expected_arg_num = max([num_of_tasks * 3 + 1, 4])
    given_arg_num = len(sys.argv) - 1
    if given_arg_num != expected_arg_num:
        print("missing arguments, given: %d expected: %d" %(given_arg_num, expected_arg_num))
        print ("expected format\n: "
               "arg1=Ntasks, arg2=task1-name, arg3=task1-context-counts, arg4=task1-valid-words ...")
        exit(1)

    word_all_dicts = []
    context_all_dicts = []
    for i in range(num_of_tasks):
        init_global_dicts()
        base = (i * 3) + 1
        task_name = sys.argv[base+1]
        data_file_name = sys.argv[base+2]
        valid_words_file = sys.argv[base+3]

        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("started task %s at %s\n" %( task_name, time))

        get_similarities(data_file_name, valid_words_file)
        words_dict, contexts_dict = get_similarities(data_file_name, valid_words_file)
        word_all_dicts.append((task_name, words_dict))
        context_all_dicts.append((task_name, contexts_dict))


    print_tables(word_all_dicts, "word_similarities", 20)
    print_tables(context_all_dicts, "strong_contexts", 20)

    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("all completed at %s\n" % time)