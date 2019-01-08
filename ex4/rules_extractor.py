import spacy_parser as parser
import utils

LOCATIONS_ADPOSITION = ["of", "to", "in", "from"]
EXCLUSIVE_LOCATIONS_ADPOSITION = ["in", "from"]

def ruled_as_person(ent):
    return worded_as_person(ent) and (lexicon_helper.does_include_first_name(ent[parser.ENT_OBJ_TEXT]) or
                                      lexicon_helper.does_include_last_name(ent[parser.ENT_OBJ_TEXT]))

def get_all_subsets_strs(main_str):
    arr = main_str.split()
    all_subsets = []
    for i in range(len(arr)):
        for stop in range(i, len(arr)):
            str = " ".join([arr[j] for j in range(i,stop+1)])
            if str.strip():
                all_subsets.append(str.strip())
    return all_subsets




def is_location_org(ent):
    return ent[parser.ENT_OBJ_SPACY_ENT].label_ == "ORG" and find_location_in_org(ent[parser.ENT_OBJ_TEXT]) != ""



def find_location_in_org(str):
    for s in get_all_subsets_strs(str):
        if lexicon_helper.is_location(s):
            return s
    return ""


def are_valid_ner(ent_tuple):
    if (ent_tuple[1][parser.ENT_OBJ_SPACY_ENT].label_ == "PERSON" or ruled_as_person(ent_tuple[1])) and \
            (ent_tuple[2][parser.ENT_OBJ_SPACY_ENT].label_ == "GPE"):
        return True
    return False

def is_close(ent_tuple):
    id = ent_tuple[0]
    ent1_to_root, ent2_to_root, joinpoint = parser.get_dependency_path_arr(ent_tuple[1], ent_tuple[2])
    if parser.get_dist(ent_tuple[1], ent_tuple[2]) < 2 and joinpoint != None:
        return True
    if parser.get_dist(ent_tuple[1], ent_tuple[2]) < 6 and joinpoint != None:
        words_between = parser.get_words_between(ent_tuple[1], ent_tuple[2])
        for w in words_between:
            if w.lemma_ in LOCATIONS_ADPOSITION:
                return True

    return False


def is_ent1_passive(ent_tuple):
    curr = ent_tuple[1][parser.ENT_OBJ_ROOT]
    length=0
    while curr.dep_ != "ROOT":
        if curr.head.pos_ == "VERB":
            last_dep= curr.dep_
        curr = curr.head
        length+=1
        if curr.pos_ == "VERB":
            verb = curr
            if length < 5 and last_dep == "dobj":
                return True
    return False


def no_old_date(ent_tuple):
    sent = ent_tuple[1][parser.ENT_OBJ_SPACY_ENT].doc
    for ne in sent.ents:
        if ne.label_ == "DATE":
            for date in ne.text.split():
                if date[-2:].lower() == "'s":
                    date = date[:-2].strip()
                if date[-1:].lower() == "s":
                    date = date[:-1].strip()
                if len(date) == 4 and is_number(date) and int(date) < 2000:
                    return False

    return True

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def valid_by_lexicon(ent_tuple):
    # if not lexicon_helper.is_location(ent_tuple[2][parser.ENT_OBJ_TEXT]):
    #     return False
    # name= ent_tuple[1][parser.ENT_OBJ_TEXT]
    # if not (lexicon_helper.does_include_first_name(name) or lexicon_helper.does_include_last_name(name)):
    #     return False
    return True


def valid_by_words(ent_tuple):
    word_before_ent1_i = ent_tuple[1][parser.ENT_OBJ_SPACY_ENT].start-1
    word_before_ent1 = ent_tuple[1][parser.ENT_OBJ_SPACY_ENT].doc[word_before_ent1_i]
    if word_before_ent1.text.lower() in LOCATIONS_ADPOSITION:
        if word_before_ent1.head.pos_ != "VERB":
            return False



    if worded_as_person(ent_tuple[2]):
        return False
    return True


def worded_as_person(ent):
    word_before_ent1_i = ent[parser.ENT_OBJ_SPACY_ENT].start-1
    word_before_ent1 = ent[parser.ENT_OBJ_SPACY_ENT].doc[word_before_ent1_i].text.lower()
    return word_before_ent1 in parser.PEOPLE_TITLES

def worded_as_location(ent):
    word_before_ent2_i = ent[parser.ENT_OBJ_SPACY_ENT].start-1
    word_before_ent2 = ent[parser.ENT_OBJ_SPACY_ENT].doc[word_before_ent2_i].text.lower()
    return word_before_ent2 in LOCATIONS_ADPOSITION


def extract_by_rules(all_ent_couples_objects):
    filterd_by_ner = []
    for ent_tuple in all_ent_couples_objects:
        if are_valid_ner(ent_tuple):
            filterd_by_ner.append(ent_tuple)

    filtered_by_words = []
    for ent_tuple in filterd_by_ner:
        if valid_by_words(ent_tuple):
            filtered_by_words.append(ent_tuple)

    valid_dates = filtered_by_words
    # for ent_tuple in filtered_by_words:
    #     if no_old_date(ent_tuple):
    #         valid_dates.append(ent_tuple)

    passed_rules = []
    for ent_tuple in valid_dates:
        if is_close(ent_tuple) or parser.is_descriptive_path(ent_tuple[1], ent_tuple[2]):
            if not is_ent1_passive(ent_tuple):
                passed_rules.append(ent_tuple)


    return passed_rules


def clean_ent_tuple_object(ent_tuple):
    sen_id = ent_tuple[0]
    ent1_text = parser.clean_entity_text(ent_tuple[1][parser.ENT_OBJ_TEXT], ent_tuple[1][parser.ENT_OBJ_ROOT])
    ent1_text = parser.modify_entity_text(ent1_text, ent_tuple[1][parser.ENT_OBJ_SPACY_ENT])
    ent2_text = parser.clean_entity_text(ent_tuple[2][parser.ENT_OBJ_TEXT], ent_tuple[2][parser.ENT_OBJ_ROOT])
    ent2_text = parser.modify_entity_text(ent2_text, ent_tuple[2][parser.ENT_OBJ_SPACY_ENT])
    return (sen_id, ent1_text, ent2_text)

lexicon_helper = None
def predict(data, _lexicon_helper):
    global lexicon_helper
    lexicon_helper = _lexicon_helper
    all_ent_couples_objects = []
    for sen_id in data:
        ent_couples_objects = parser.get_ent_objects_from_sen(sen_id, data[sen_id])
        all_ent_couples_objects += ent_couples_objects

    all_ent_couples_objects = sorted(all_ent_couples_objects, key=utils.get_senid_int)
    good_ent_couples_objects = extract_by_rules(all_ent_couples_objects)
    cleaned = [clean_ent_tuple_object(obj) for obj in good_ent_couples_objects]
    return cleaned


