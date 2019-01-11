import sys
from collections import defaultdict

import os

import utils
from utils import are_similar


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
            if gold:
                if all_lines.has_key(sen_id):
                    all_id_relations = all_lines.get(sen_id)
                    for line_i in all_id_relations:
                        if line_i == line_arr:
                            break
                        else:
                            all_lines[sen_id].append(line_arr)
                            break
                else:
                    all_lines[sen_id].append(line_arr)
            else:
                all_lines[sen_id].append(line_arr)
    return all_lines


def compare_values(sen_id, gold_values, pred_values):
    TP_sent = []
    FP_sent = []
    TP = FP = 0
    match = False

    for pred_val in pred_values:
        for gold_val in gold_values:
            if are_similar(gold_val[utils.NER1], pred_val[utils.NER1]) and \
                    are_similar(gold_val[utils.RE], pred_val[utils.RE]) and \
                    are_similar(gold_val[utils.NER2], pred_val[utils.NER2]):
                TP += 1
                string = sen_id + "\t" + '\t'.join(pred_val)
                TP_sent.append(string)
                match = True
                gold_values.remove(gold_val)
                break
        if not match:
            FP += 1
            string = sen_id + "\t" + '\t'.join(pred_val)
            FP_sent.append(string)
        match = False

    # sanity
    if TP+FP > len(pred_values):
        print "ERROR in compare_values()"

    return TP, FP, TP_sent, FP_sent


def get_stat(gold_annotation_data, pred_annotation_data):
    TP = FP = FN = 0.0
    TP_sents = []
    FP_sents = []
    FN_sents = []

    for pred_sen_id, pred_value in pred_annotation_data.iteritems():
        if gold_annotation_data.has_key(pred_sen_id):
            gold_value = gold_annotation_data[pred_sen_id]
            this_TP, this_FP, this_TP_sent, this_FP_sent = compare_values(pred_sen_id, gold_value, pred_value)
            TP += this_TP
            FP += this_FP
            TP_sents += this_TP_sent
            FP_sents += this_FP_sent
        else:
            FP += len(pred_value)
            for val in pred_value:
                string = pred_sen_id + "\t" + '\t'.join(val)
                FP_sents.append(string)

    for gold_sen_id, gold_value in gold_annotation_data.iteritems():
        for val in gold_value:
            string = gold_sen_id + "\t" + '\t'.join(val)
            FN_sents.append(string)
        FN += len(gold_value)

    return TP, FP, FN, TP_sents, FP_sents, FN_sents


def print_stats(TP, FP, FN):
    print "TP: " + str(TP)
    print "FP: " + str(FP)
    print "FN: " + str(FN)

    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    if (recall + precision) > 0:
        f1 = 2 * (recall * precision) / (recall + precision)
    else:
        f1 = 0

    print
    print ("Precision = %.4f%%" % (precision * 100))
    print ("Recall = %.4f%%" % (recall * 100))
    print ("F1 = %.4f%%" % (f1 * 100))


def write2file(sentences, file_name):
    sent_ids = []
    for sent in sentences:
        sent_id = sent.split()[0]
        sent_ids.append(sent_id)
    sorted_ids = utils.get_sorted_ids(sent_ids)

    with open(file_name, 'w') as f:
        for sorted_sent_id in sorted_ids:
            for sent in sentences:
                sent_id = sent.split()[0]
                if sent_id == sorted_sent_id:
                    sentences.remove(sent)
                    f.write(sent)
                    break


def write_stat2file(TP_sents, FP_sents, FN_sents):
    if not os.path.exists("statistics"):
        os.makedirs("statistics")
    write2file(TP_sents, 'statistics/TP.txt')
    write2file(FP_sents, 'statistics/FP.txt')
    write2file(FN_sents, 'statistics/FN.txt')


if __name__ == '__main__':
    gold_annotation_file = sys.argv[1]
    pred_annotation_file = sys.argv[2]

    gold_annotation_data = get_annotation_data(gold_annotation_file, gold=True)
    pred_annotation_data = get_annotation_data(pred_annotation_file, gold=False)

    TP, FP, FN, TP_sents, FP_sents, FN_sents = get_stat(gold_annotation_data, pred_annotation_data)

    print_stats(TP, FP, FN)
    write_stat2file(TP_sents, FP_sents, FN_sents)


