import sys
import os

word_count_dict = {}
word_to_lexicon_dict = {}
tagged_extracted_features = []
ignore_files = []
english_words = set()

def create_word_count_dict(input_file_name):
    with open(input_file_name) as f:
        content = f.readlines()

    wc_dict = {}
    content=[x.strip() for x in content]
    for line in content:
        pairs = line.split(" ")
        for pair in pairs:
            arr = pair.rsplit("/", 1)
            word = arr[0]
            tag = arr[1]
            if word in wc_dict:
                wc_dict[word] += 1
            else:
                wc_dict[word] = 1
    return wc_dict


def get_features_by_word(word, is_rare):
    feature_str = ""

    if is_rare:
        if len(word) >= 4:
            feature_str += " pref4=%s" % word[:4]
            feature_str += " suff4=%s" % word[-4:]
        if len(word) >= 3:
            feature_str += " pref3=%s" % word[:3]
            feature_str += " suff3=%s" % word[-3:]
        if len(word) >= 2:
            feature_str += " pref2=%s" % word[:2]
            feature_str += " suff2=%s" % word[-2:]
        if len(word) >= 1:
            feature_str += " pref1=%s" % word[:1]
            feature_str += " suff1=%s" % word[-1:]

        if "-" in word:
            feature_str += " hashyph=1"
        if (any(x.isupper) for x in word):
            feature_str += " hassupper=1"
        if (any(x.isdigit()) for x in word):
            feature_str += " hasdigit=1"
    else:
        feature_str += " form=%s" % word

    return feature_str


def get_features_by_2_prevs(prev_prev_arr, prev_arr):
    prev_prev_word = prev_prev_arr[0]
    prev_prev_tag = prev_prev_arr[1]
    prev_word = prev_arr[0]
    prev_tag = prev_arr[1]
    feature_str = ""
    if prev_prev_word is not None:
        feature_str += " wi-2=%s" % prev_prev_word
        feature_str += " wi-1=%s" % prev_word
    elif prev_word is not None:
        feature_str += " wi-1=%s" % prev_word

    feature_str += " " + get_feat_str_by_prevtag(prev_tag)
    feature_str += " " + get_feat_str_by_2prevs(prev_prev_tag, prev_tag)

    return feature_str


def get_feat_str_by_2prevs(prev_prev_tag, prev_tag):
    return "ti-2ti-1=%s%s" % (prev_prev_tag, prev_tag)


def get_feat_str_by_prevtag(prev_tag):
    return "ti-1=%s" % prev_tag


def get_features_by_next_word(arr):
    word = arr[0]
    if word is not None:
        return " w+1=%s" % word
    else:
        return ""


def get_features_by_next_next_word(arr):
    word = arr[0]
    if word is not None:
        return " w+2=%s" % word
    else:
        return ""


def get_clean_line_arr(tagged_line):
    line_arr = map(lambda tagged_word: tagged_word.rsplit("/",1)[0] ,tagged_line.split())
    return line_arr

def get_features_by_lexicons(word, line_arr, word_index):


    feat_str = ""
    if word in word_to_lexicon_dict:
        for lexicon in word_to_lexicon_dict[word]:
            dict = word_to_lexicon_dict[word][lexicon]
            lex_line_arr = dict["line"].split()
            lex_index = dict["index"]
            if word_index < lex_index or (len(line_arr) -word_index) < (len(lex_line_arr)-lex_index):
                continue

            linestart = word_index - lex_index
            line_match=True
            for i in range(len(lex_line_arr)):
                if lex_line_arr[i] != line_arr[linestart+i]:
                    line_match = False
            if line_match:
                feat_str += " lexicon=%s" % lexicon

    return feat_str


def get_tagged_extracted_features(input_file_name):
    feature_strings = []
    with open(input_file_name) as f:
        content = f.readlines()

    content = [x.strip() for x in content]
    for line_number in range(len(content)):
        line = content[line_number]
        pairs = line.split(" ")
        for word_number in range(len(pairs)):
            pair = pairs[word_number]
            arr = pair.rsplit("/", 1)
            word = arr[0]
            tag = arr[1]
            if word_number == 0:
                prev_arr = [None, 'start']
                prev_prev_arr = [None, 'start',]
            elif word_number == 1:
                prev_arr = pairs[word_number-1].rsplit("/",1)
                prev_prev_arr = [None, 'start']
            else:
                prev_arr = pairs[word_number-1].rsplit("/",1)
                prev_prev_arr = pairs[word_number-2].rsplit("/",1)

            if word_number == (len(pairs) - 1):
                next_arr = [None,None]
                next_next_arr = [None, None]
            elif word_number == (len(pairs) - 2):
                next_arr = pairs[word_number + 1].rsplit("/",1)
                next_next_arr = [None, None]
            else:
                next_arr = pairs[word_number + 1].rsplit("/",1)
                next_next_arr = pairs[word_number + 2].rsplit("/",1)


            is_rare = word not in word_count_dict or word_count_dict[word] < 5
            feature_str = "%s" % tag
            feature_str += get_features_by_word(word, is_rare)
            feature_str += get_features_by_2_prevs(prev_prev_arr, prev_arr)
            feature_str += get_features_by_next_word(next_arr)
            feature_str += get_features_by_next_next_word(next_next_arr)
            clean_line_arr = get_clean_line_arr(line)
            feature_str += get_features_by_lexicons(word, clean_line_arr, word_number)
            feature_strings.append(feature_str)

    return feature_strings


def print_feature_file(tagged_extracted_features, output_file_name):
    with open(output_file_name, "w") as output:
        for i in range(len(tagged_extracted_features)):
            line = tagged_extracted_features[i]
            output.write("%s\n" % line)
        pass
    pass


def load_lexicons(lexicon_dir):

    for filename in os.listdir(lexicon_dir):
        if filename in (ignore_files ):
            continue

        with open(os.path.join(lexicon_dir, filename)) as f:
            content = f.readlines()

        content = [x.strip() for x in content]
        for line in content:
            words = line.split()
            for i in range(len(words)):
                word = words[i]
                if word not in word_to_lexicon_dict:
                    word_to_lexicon_dict[word] = {}

                word_to_lexicon_dict[word][filename] = {}
                word_to_lexicon_dict[word][filename]["line"] = line
                word_to_lexicon_dict[word][filename]["index"] = i


if __name__ == '__main__':
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
    lexicon_dir = sys.argv[3]

    word_count_dict = create_word_count_dict(input_file_name)
    load_lexicons(lexicon_dir)
    tagged_extracted_features = get_tagged_extracted_features(input_file_name)
    print_feature_file(tagged_extracted_features, output_file_name)
