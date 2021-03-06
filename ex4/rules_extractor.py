import spacy_parser as parser
import utils

# nltk.download('wordnet')
# from nltk.corpus import wordnet as wn

LOCATIONS_ADPOSITION = ["of", "to", "in", "from"]
EXCLUSIVE_LOCATIONS_ADPOSITION = ["in", "from"]

def ruled_as_person(ent):
    return worded_as_person(ent)

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
            (ent_tuple[2][parser.ENT_OBJ_SPACY_ENT].label_ == "GPE" or
                     ent_tuple[2][parser.ENT_OBJ_SPACY_ENT].label_ == "LOC" or
                 (lexicon_helper.is_location((ent_tuple[2]))) or
                         ent_tuple[2][parser.ENT_OBJ_SPACY_ENT].label_ == "NORP" and
                     lexicon_helper.valid_norps((ent_tuple[2]))):
        return True
    return False


# def is_like_kill(ent_tuple):
#
#     murder_v = wn.synset('murder.v.01')
#     murder_n = wn.synset('murder.n.01')
#     curr = ent_tuple[1][parser.ENT_OBJ_ROOT]
#     while curr.dep_ != "ROOT":
#         syns  = wn.synsets(curr.lemma_)
#         for s in syns:
#             if s.path_similarity(murder_v) >= 0.5 or s.path_similarity(murder_n) >= 0.5:
#                 return True
#         curr = curr.head
#
#     return False


def no_old_date(ent_tuple):
    sent = ent_tuple[1][parser.ENT_OBJ_SPACY_ENT].doc
    for ne in sent.ents:
        if ne.label_ == "DATE":
            for date in ne.text.split():
                if date[-2:].lower() == "'s":
                    date = date[:-2].strip()
                if date[-1:].lower() == "s":
                    date = date[:-1].strip()
                if len(date) == 4 and is_number(date) and int(date) < 1900:
                    return False

    return True


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


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
    passed_rules = all_ent_couples_objects

    #valid ner
    passed_rules = filter(lambda t: are_valid_ner(t), passed_rules)


    # for t in passed_rules:
    #     path = parser.get_dependecy_path_str_with_words(t[1], t[2])
    #     print("sent id: " + t[0])
    #     print ("sent is: " + t[1][parser.ENT_OBJ_SPACY_ENT].doc.text)
    #     print ("graph is: " + path)
    #     pass

    # valid surrounding words - not good
    # passed_rules = filter(lambda t: valid_by_words(t), passed_rules)

    # #no old dates
    passed_rules = filter(lambda t: no_old_date(t), passed_rules)


    direct_path_sents = filter(lambda t: parser.is_descriptive_path(t[1], t[2]), passed_rules)

    # #be sentences and lives sentences
    be_senentces = filter(lambda t: parser.is_be_sentence(t[1], t[2]), passed_rules)


    merged = utils.filter_duplicate_entities( direct_path_sents + be_senentces )
    passed_rules = merged

    # filter kills
    # passed_rules = [x for x in passed_rules if not is_like_kill(x)]


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


