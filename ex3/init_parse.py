import sys
from collections import Counter

import datetime

CONTEXT_TEGSET = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',  # Verb
                'NN', 'NNP', 'NNPS', 'NNS',  # Noun
                'JJ', 'JJR', 'JJS',  # Adjective
                'RB', 'RBR', 'RBS'}  # Adverb

word_counts = Counter()

def all_sentence_parse(input_data, output_file):
    """
    print to 'output_file': every word with its all context word
    :param input_data:
    :param output_file:
    :return:
    """
    with open(input_data, 'r') as f_in:
        with open(output_file, 'w') as f_out:
            file_lines = f_in.readlines()
            sentence_lines = []
            for file_line_i in range(len(file_lines)):
                file_line = file_lines[file_line_i]
                stripped = file_line.strip()
                if stripped:  # if not blank line
                   sentence_lines.append(file_line)
                else:  # process
                    for word_i in range(len(sentence_lines)):
                        line = sentence_lines[word_i].split()
                        word = line[2]  # lemma
                        word_tag = line[4] # lemma's tag
                        if word_tag in CONTEXT_TEGSET:
                            word_counts[word] += 1
                            for context_i in range(len(sentence_lines)):
                                if(word_i != context_i):
                                    context_line = sentence_lines[context_i].split()
                                    context = context_line[2]  # lemma
                                    context_tag = context_line[4]  # lemma's tag
                                    if context_tag in CONTEXT_TEGSET:
                                        string2file = word + ' ' + context + '\n'
                                        f_out.write(string2file)
                    sentence_lines = []



def getWindow(start_line, file_lines, word):
    prevprev_context = None
    prev_context = None
    next_context = None
    nextnext_context = None

    i_back = 0
    while (start_line - i_back != 0):
        line = file_lines[start_line - i_back - 1].split()
        if line:
            i_back += 1
            line_i = file_lines[start_line - i_back].split()
            context = line_i[2]  # lemma
            word_tag = line_i[4]  # lemma's tag
            if (word_tag in CONTEXT_TEGSET) and (word != context):
                if prev_context is None:
                    prev_context = context
                else:
                    prevprev_context = context
                    break
        else:
            break

    i_next = 0
    while (start_line + i_next != len(file_lines)):
        line = file_lines[start_line + i_next + 1].split()
        if line:
            i_next += 1
            line_i = file_lines[start_line + i_next].split()
            context = line_i[2]  # lemma
            word_tag = line_i[4]  # lemma's tag
            if (word_tag in CONTEXT_TEGSET) and (word != context):
                if next_context is None:
                    next_context = context
                else:
                    nextnext_context = context
                    break
        else:
            break

    return prevprev_context, prev_context, next_context, nextnext_context


def window_parse(input_data, output_file):
    with open(input_data, 'r') as f_in:
        with open(output_file, 'w') as f_out:
            file_lines = f_in.readlines()
            line_words = set()
            for file_line_i in range(len(file_lines)):
                file_line = file_lines[file_line_i]
                line = file_line.split()
                if line:  # if not blank line
                    word = line[2]  # lemma
                    word_tag = line[4] # lemma's tag
                    if word_tag in CONTEXT_TEGSET:
                        word_counts[word] += 1
                        # if word appeared twice (or more) in sentence, don't add it twice (or more) and move to the next word
                        if word not in line_words:
                            line_words.add(word)
                            prevprev_context, prev_context, next_context, nextnext_context = getWindow(file_line_i, file_lines, word)
                            string2file1 = word + ' ' + str(prevprev_context) + '\n'
                            string2file2 = word + ' ' + str(prev_context) + '\n'
                            string2file3 = word + ' ' + str(next_context) + '\n'
                            string2file4 = word + ' ' + str(nextnext_context) + '\n'
                            f_out.write(string2file1)
                            f_out.write(string2file2)
                            f_out.write(string2file3)
                            f_out.write(string2file4)
                else:  # move to the next word
                    line_words = set()


def dependency_parse(input_data, output_file):
    sentence_lines = []
    with open(input_data, 'r') as f_in:
        with open(output_file, 'w') as f_out:
            file_lines = f_in.readlines()
            for file_line in file_lines:
                line = file_line.split()
                if line:
                    sentence_lines.append(line)
                else:
                    #proccesing all senetence lines here
                    this_line_word_context = [] #list not set or dict. to include reocurrence of word in same sentence
                    for line_fields in sentence_lines:
                        word = line_fields[2]
                        word_tag = line_fields[4]
                        head = int(line_fields[6])
                        head_tag = sentence_lines[head-1][4]
                        head_word = sentence_lines[head - 1][2]
                        deprel = line_fields[7]
                        if word_tag in CONTEXT_TEGSET:
                            if head != 0:  # ROOT
                                word_counts[word] += 1
                                att1 = head_word + "|" + deprel + "|<"  # < is relation direction
                                att2 = word + "|" + deprel + "|>"  # < is relation direction
                                # we add all contexts to word
                                this_line_word_context.append((word, att1))
                                this_line_word_context.append((head_word, att2))
                                if head_tag == 'IN':
                                    head_head_ID = int(sentence_lines[head - 1][6])
                                    head_head_word = sentence_lines[head_head_ID-1][2]
                                    att1 = head_head_word + "|" + deprel + "|" + head_word + "|<"
                                    att2 = word + "|" + deprel + "|" + head_word + "|>"
                                    # we add all contexts to word
                                    this_line_word_context.append((word, att1))
                                    this_line_word_context.append((head_head_word, att2))


                    # finished processing sentence
                    for (w,c) in this_line_word_context:
                        string2file = w + ' ' + c + '\n'
                        f_out.write(string2file)
                    sentence_lines = []  # clear sentence lines


if __name__ == '__main__':
    print(datetime.datetime.now())
    parse_type = sys.argv[1]
    input_data = sys.argv[2]
    output_file = sys.argv[3]
    output_words_file = sys.argv[4]
    word_min_num = int(sys.argv[5])

    if parse_type == 'all':
        all_sentence_parse(input_data, output_file)
    elif parse_type == 'window':
        window_parse(input_data, output_file)
    elif parse_type == 'dep':
        dependency_parse(input_data, output_file)

    with open(output_words_file, "w") as f:
        for w in word_counts:
            count = word_counts[w]
            if count > word_min_num:
                f.write("%s %d\n" % (w, count))

    print(datetime.datetime.now())

