from hmm2.GreedyTag import append_missing_unk_tags_with_1
from hmm2.GreedyTag import load_e_mle
from hmm2.GreedyTag import load_q_mle
from hmm2.GreedyTag import singles_dict


def create_impossible_seqs():
    impossible_seqs = set()
    for prev_tag in singles_dict:
        if prev_tag != 'start':
            impossible_seqs.add((prev_tag, 'start'))
        if is_special_char(prev_tag) and prev_tag != '\'' and prev_tag != '\"':
            impossible_seqs.add((prev_tag, 'POS'))

    impossible_seqs.add(('TO','TO'))
    impossible_seqs.add(('TO','POS'))
    impossible_seqs.add(('POS','POS'))
    impossible_seqs.add(('PDT','POS'))
    impossible_seqs.add(('PDT','PDT'))
    return impossible_seqs


def print_seqs(impossible_seqs, file_name):
    output = open(file_name, 'w')
    for seq in impossible_seqs:
        output.write("%s %s\n" % (seq[0], seq[1]))
    output.close()


def is_special_char(tag):
    if len(tag) <=2 and not tag.isalpha():
        return True
    return False



if __name__ == '__main__':
    load_e_mle("e.mle")
    load_q_mle("q.mle")
    append_missing_unk_tags_with_1()
    impossible_seqs = create_impossible_seqs()
    print_seqs(impossible_seqs, "extra_args")