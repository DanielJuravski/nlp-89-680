import sys
from collections import Counter

CONTEXT_TEGSET = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',  # Verb
                'NN', 'NNP', 'NNPS', 'NNS',  # Noun
                'JJ', 'JJR', 'JJS',  # Adjective
                'RB', 'RBR', 'RBS'}  # Adverb


'''
Notice we use only lemma word of the form,
using word form but counting by lemmas gives nteresting reults (i think better)
This requires changing word_counts to {lemma_word:{form1:count_form1, form2:count_form2}}
and printing all word forms when sum of lemma words are above word_min_num
'''
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
            start_line = 0
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
                            for in_line_i in range(start_line, start_line+9999):
                                in_line = file_lines[in_line_i]
                                in_line = in_line.split()
                                if in_line:  # if not blank line
                                    context = in_line[2]  # lemma
                                    word_tag = in_line[4]  # lemma's tag
                                    if word_tag in CONTEXT_TEGSET:
                                        if word != context:  # if context word is not the word we work on it
                                            string2file = word + ' ' + context + '\n'
                                            f_out.write(string2file)
                                            #print string2file
                                else:
                                    break
                else:  # move to the next word
                    start_line = file_line_i+1
                    line_words = set()


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
            start_line = 0
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
                            #print string2file
                else:  # move to the next word
                    start_line = file_line_i+1
                    line_words = set()


def dependency_parse(input_data, output_file):
    word_contexts = {}
    sentence_lines = []
    with open(input_data, 'r') as f_in:
        with open(output_file, 'w') as f_out:
            file_lines = f_in.readlines()
            for file_line in file_lines:
                if file_line:
                    sentence_lines.append(file_line)
                else:
                    #proccesing all senetence lines here
                    line_words = [] #list not set or dict. to include reocurrence of word in same sentence
                    for i in range(len(sentence_lines)):
                        word_line = sentence_lines[i].split()
                        word = word_line[1]
                        word_contexts = []
                        for j in sentence_lines:
                            if i != j:
                                context_line = sentence_lines[i].split()
                                context_word = context_line[1]
                                #1) check if there is an edge between context and word or vice versa
                                #if so -> word_contexts.append((context_word, direction))

                                #2)if context is preposition then also add the below
                                #concat lemma form of proposition to the word it relates to
                                # if target word is president and we have 'president with the apple'
                                # current context word is with than we also add
                                #  word_contexts.append((withapple, direction))


                        #we add all contexts to word
                        line_words.append((word, word_contexts))

                    #finished processing sentence
                    for (w,c) in line_words:  #fill main dictionary word_contexts
                        w_contexts = word_contexts.get(w, Counter()) #get counter or new counter
                        for context in c:
                            word_contexts[context] += 1
                        word_contexts[w] = w_contexts
                    sentence_lines = [] #clear sentence lines


if __name__ == '__main__':
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




