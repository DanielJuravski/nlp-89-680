import sys
from collections import Counter
import numpy as np
import operator
from close_words import TARGET_WORDS

p_word_dict = {}
p_att_dict = {}
p_word_att_dict = {}

def safe_div(x,y):
    if y == 0:
        return 0
    return x / float(y)


def PMI(u_att_count, u_att_total_count, u_count, u_total_count, att_count, att_total_count):
    p_u_att = safe_div(u_att_count, u_att_total_count)
    p_u = safe_div(u_count, u_total_count)
    p_att = safe_div(att_count, att_total_count)

    cond_pmi = safe_div(p_u_att, (p_u*p_att))
    cond_pmi = np.log(cond_pmi)

    pmi = np.max((0, cond_pmi))

    return pmi, p_u_att, p_u, p_att

def getGood(good_words_file):
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

    good_words_dict = getGood(good_words_file)

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
    total_words_count = sum(total_word_occurrence_count.values())
    total_context_count = sum(total_context_occurrence_count.values())
    total_word_context_count = sum([sum(main_dict[x].values()) for x in main_dict])


    for word in main_dict:
        total_PMI = 0
        all_word_context = main_dict[word]
        for word_context in all_word_context:
            word_context_occurrence = all_word_context[word_context]
            word_count = total_word_occurrence_count[word]
            context_count = total_context_occurrence_count[word_context]
            #word_context_PMI = PMI(word_context_occurrence, total_word_context_occurrence_count,
            #                       word_count, total_words_count,
            #                       context_count, total_context_count)
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
            #print att
            for word in attribute_dict[att]:
                word_attributes = main_dict[word]
                if att in word_attributes:
                    DT[word] += u_attributes[att] * word_attributes[att]

        sorted_DT = sorted(DT.items(), key=operator.itemgetter(1), reverse=True)
        final_words = sorted_DT[:num_of_words]
        return [x[0] for x in final_words]


    else:
        print "ERROR: no word '" + u + "' in main_dict !"

    pass

def find_highest_contexts(target_word, main_dict, max_attributes):
    if target_word in main_dict:
        print "Word '" + target_word + "' found in main_dict ..."
        target_word_attributes = main_dict[target_word]
        sorted_attributes = sorted(target_word_attributes.items(), key=operator.itemgetter(1), reverse=True)
        return [x[0] for x in sorted_attributes[:max_attributes]]




if __name__ == '__main__':
    if len(sys.argv) > 1:
        data_file_name = sys.argv[1]
        good_words_file = sys.argv[2]
    else:
        data_file_name = 'data/huge_sorted'
        good_words_file = 'data/huge_words'
        # data_file_name = 'parsed_data/huge_sample_sorted'

    main_dict, attribute_dict = loadData(data_file_name, good_words_file)

    # #debug
    # TARGET_WORDS=['University', 'performed']

    for target_word in TARGET_WORDS:
        similar_words = findSimilar(target_word, main_dict, attribute_dict, 20)
        print "target word is: " + target_word
        for i, w in enumerate(similar_words):
            print("----close word no %d: %s" % (i, w))

        highest_contexts = find_highest_contexts(target_word, main_dict, 20)
        for i, w in enumerate(highest_contexts):
            print("----context no %d: %s" % (i, w))


