import sys
from collections import defaultdict
import copy
import collections


import utils



def get_annotation_data(annotation_file, gold):
    with open(annotation_file, 'r') as f:
        all_lines = defaultdict(list)
        for line in f:
            line_arr = []
            sen_id, ner1, relation_type, ner2, sen = line.split('\t')
            if gold and relation_type != utils.OUR_RE:
                continue
            line_arr.append(ner1)
            line_arr.append(relation_type)
            line_arr.append(ner2)
            line_arr.append(sen)
            # check if that NER1 RE NER2 already exist
            # if all_lines.has_key(sen_id):
            #     all_id_relations = all_lines[sen_id]
            #     for line_i in all_id_relations:
            #         if line_i == line_arr:
            #             break
            #         else:
            #             all_lines[sen_id].append(line_arr)
            #             break
            # else:
            #     all_lines[sen_id].append(line_arr)
            all_lines[sen_id].append(line_arr)
    return all_lines


def compare_values(sen_id, gold_values, pred_values):
    with open('statistics/TP.txt', 'a') as f_TP:
        with open('statistics/FP.txt', 'a') as f_FP:
            gold = (gold_values)
            pred = (pred_values)
            TP = FP = FN = 0
            match = False
            for pred_val in pred:
                for gold_val in gold:
                    if gold_val[utils.NER1] == pred_val[utils.NER1] and \
                            gold_val[utils.RE] == pred_val[utils.RE] and \
                            gold_val[utils.NER2] == pred_val[utils.NER2]:
                        TP += 1
                        string = sen_id + " " + ' '.join(pred_val)
                        f_TP.write(string)
                        match = True
                        gold.remove(gold_val)
                        break
                if not match:
                    FP += 1
                    string = sen_id + " " + ' '.join(pred_val)
                    f_FP.write(string)
                match = False

            # sanity
            if TP+FP > len(pred_values):
                print "ERROR in compare_values()"

    return TP, FP, FN


def get_stat(gold_annotation_data, pred_annotation_data):
    TP = FP = FN = 0.0
    open('statistics/TP.txt', 'w').close()
    open('statistics/FP.txt', 'w').close()
    open('statistics/FN.txt', 'w').close()

    for pred_sen_id, pred_value in pred_annotation_data.iteritems():
        if gold_annotation_data.has_key(pred_sen_id):
            gold_value = gold_annotation_data[pred_sen_id]
            this_TP, this_FP, this_FN = compare_values(pred_sen_id, gold_value, pred_value)
            TP += this_TP
            FP += this_FP
            FN += this_FN
        else:
            FP += len(pred_value)

    with open('statistics/FN.txt', 'a') as f_FN:
        for gold_sen_id, gold_value in gold_annotation_data.iteritems():
            for val in gold_value:
                string = gold_sen_id + " " + ' '.join(val)
                f_FN.write(string)
            FN += len(gold_value)

    return TP, FP, FN


if __name__ == '__main__':
    if len(sys.argv) > 2:
        gold_annotation_file = sys.argv[1]
        pred_annotation_file = sys.argv[2]
    else:
        gold_annotation_file = 'data/TRAIN.annotations'
        gold_annotation_file = 'data/DEMO_TRAIN.annotations'
        pred_annotation_file = 'data/DEMO_PRED.annotations'

    gold_annotation_data = get_annotation_data(gold_annotation_file, gold=True)
    pred_annotation_data = get_annotation_data(pred_annotation_file, gold=False)

    TP, FP, FN = get_stat(gold_annotation_data, pred_annotation_data)

    print "TP: " + str(TP)
    print "FP: " + str(FP)
    print "FN: " + str(FN)

    precision = TP/(TP+FP)
    recall = TP/(TP+FN)
    f1 = 2*(recall * precision) / (recall + precision)

    print
    print "Precision = " + str(precision)
    print "Recall = " + str(recall)
    print "F1 = " + str(f1)
