import sys

from memm2.MEMMTag import LINES_START, LINES_LIMIT

def compare_predictions_to_answers(predictions_file, answers_file):
    with open(answers_file) as answers_f:
        with open(predictions_file) as pred_f:
            answers_content=answers_f.readlines()
            answers_content=[x.strip() for x in answers_content]
            pred_content=pred_f.readlines()
            pred_content=[x.strip() for x in pred_content]
            bad_results = 0
            good_results = 0
            line_num = 0
            for answer_line in answers_content:
                if line_num < LINES_START-1:
                    continue
                if line_num > LINES_LIMIT-1:
                    break
                pred_line = pred_content[line_num]
                line_num += 1
                answer_pairs = answer_line.split()
                pred_pairs = pred_line.split()
                for j in range(len(answer_pairs)):
                    answer_arr = answer_pairs[j].rsplit("/",1)
                    pred_arr = pred_pairs[j].rsplit("/",1)
                    if answer_arr[0] != pred_arr[0]:
                        print("mismatched words in line %d word %d" % (line_num,j))
                    answer_tag=answer_arr[1]
                    pred_tag=pred_arr[1]
                    if answer_tag == pred_tag:
                        good_results += 1
                    else:
                        print("bad result in line %d word %d" % (line_num, j))
                        print("word: " + answer_arr[0])
                        print("our tag: " +pred_tag)
                        print("true tag: "+answer_tag)
                        bad_results += 1

    return (good_results, bad_results)


if __name__ == '__main__':
    our_output_file = sys.argv[1]
    tagged_file = sys.argv[2]

    (good_results, bad_results) = compare_predictions_to_answers(our_output_file, tagged_file)
    print "good results = " + repr(good_results)
    print "bad results = " + repr(bad_results)
    print "precentage = " + repr(float(good_results) * 100 / (good_results + bad_results))

