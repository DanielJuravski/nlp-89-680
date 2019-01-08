import spacy_parser as parser
import utils


def are_valid_ner(ent_tuple):
    if ent_tuple[1][parser.ENT_OBJ_SPACY_ENT].label_ == "PERSON" and \
                    ent_tuple[2][parser.ENT_OBJ_SPACY_ENT].label_ == "GPE":
        return True
    return False

def is_close(ent_tuple):
    id = ent_tuple[0]
    # return parser.is_descriptive_path(ent_tuple[1], ent_tuple[2])

    ent1_to_root, ent2_to_root, joinpoint = parser.get_dependency_path_arr(ent_tuple[1], ent_tuple[2])
    if parser.get_dist(ent_tuple[1], ent_tuple[2]) < 2 and joinpoint != None:
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
            date = ne.text
            if date[:len("the")].lower() == "the":
                date=date[len("the"):].strip()
            if date[-2:].lower() == "'s":
                date = date[:-2].strip()
            if date[-1:].lower() == "s":
                date = date[:-1].strip()
            if len(date) == 4 and int(date) < 2000:
                return False

    return True


def valid_by_lexicon(ent_tuple):
    if not lexicon_helper.is_location(ent_tuple[2][parser.ENT_OBJ_TEXT]):
        return False
    name= ent_tuple[1][parser.ENT_OBJ_TEXT]
    if not (lexicon_helper.does_include_first_name(name) or lexicon_helper.does_include_last_name(name)):
        return False
    return True

def extract_by_rules(all_ent_couples_objects):
    filterd_by_ner = []
    for ent_couples_object in all_ent_couples_objects:
        if are_valid_ner(ent_couples_object):
            filterd_by_ner.append(ent_couples_object)

    filtered_by_lexicon = []
    for ent_tuple in filterd_by_ner:
        if valid_by_lexicon(ent_tuple):
            filtered_by_lexicon.append(ent_tuple)

    valid_dates = []
    for ent_tuple in filtered_by_lexicon:
        if no_old_date(ent_tuple):
            valid_dates.append(ent_tuple)

    passed_rules = []
    for ent_couples_object in valid_dates:
        if is_close(ent_couples_object):
            if not is_ent1_passive(ent_couples_object):
                passed_rules.append(ent_couples_object)


    return passed_rules


def clean_ent_tuple_object(ent_tuple):
    sen_id = ent_tuple[0]
    ent1_text = parser.clean_entity_text(ent_tuple[1][parser.ENT_OBJ_TEXT], ent_tuple[1][parser.ENT_OBJ_ROOT])
    ent1_text = parser.modify_entity_text(ent1_text, ent_tuple[1][parser.ENT_OBJ_ROOT])
    ent2_text = parser.clean_entity_text(ent_tuple[2][parser.ENT_OBJ_TEXT], ent_tuple[2][parser.ENT_OBJ_ROOT])
    ent2_text = parser.modify_entity_text(ent2_text, ent_tuple[2][parser.ENT_OBJ_ROOT])
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


