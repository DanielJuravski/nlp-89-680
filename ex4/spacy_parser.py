SPLIT_ROOTS = "root1|root2"
JOINPOINT = "joinpoint"
LIVE_IN = "Live_In"

ENT_OBJ_ROOT = "ent_obj_root"
ENT_OBJ_TEXT = "ent_obj_text"
ENT_OBJ_LABEL = "ent_obj_label"
ENT_OBJ_SPACY_ENT = "ent_obj_spacy_ent"

PEOPLE_TITLES = ["mr.", "mrs.", "ms.", "prince", "sir", "sultan", "lord"]


#Todo move to clean text
def get_entity_text(text, root):
    ent_text = text.strip()
    left_edge_word = root.left_edge.text
    if left_edge_word.lower() in PEOPLE_TITLES:
        ent_text = left_edge_word + " " + ent_text

    text_arr = text.split()
    if text_arr[0].lower() == "the":
        ent_text = " ".join(text_arr[1:])

    if ent_text[-2:].lower() == "'s":
        ent_text = ent_text[:-2].strip()
    return ent_text


def get_xs_from_sen(sen_id, sen):
    """

    :param sen_id:
    :param sentence:
    :return array of tuples (sen_id, ent1, ent2):
    """
    xs = []
    entities = []
    for ent in sen.doc.ents:
        ent_text = get_entity_text(ent.text, ent.root)
        ent_obj = {ENT_OBJ_ROOT: ent.root, ENT_OBJ_TEXT: ent_text, ENT_OBJ_LABEL: ent.label_, ENT_OBJ_SPACY_ENT:ent}
        entities.append(ent_obj)



    for i, ent_i in enumerate(entities):
        for j, ent_j in enumerate(entities):
            if i != j:
                xs.append((sen_id, ent_i, ent_j))

    return xs


def get_x_data(feature_extractor, data):
    all_x_ent_tuples_data = []
    for sen_id in data:
        sentence_x_data = get_xs_from_sen(sen_id,data[sen_id])
        all_x_ent_tuples_data += sentence_x_data

    all_x_data = []
    for ent_tuple in all_x_ent_tuples_data:
        extracted_x = feature_extractor.extract_features(ent_tuple, data[ent_tuple[0]])
        all_x_data.append(extracted_x)

    sen_entities, x_data = feature_extractor.build_x_vectors(all_x_data)
    return sen_entities

def get_words_between(ent1, ent2):
    words = []
    root1_index = ent1[ENT_OBJ_ROOT].i
    root2_index = ent2[ENT_OBJ_ROOT].i
    sent = ent1[ENT_OBJ_ROOT].doc

    start = min([root1_index, root2_index])
    stop = max([root1_index, root2_index])
    start_i = sent[start].right_edge.i
    stop_i = sent[stop].left_edge.i
    for i in range(start_i, stop_i + 1):
        words.append(sent[i].text)

    return words


def is_split_roots(dependency_path_str):
    return SPLIT_ROOTS in dependency_path_str


def is_anccestor(dependency_path_str, ent_number):
    if ent_number == 1:
        return dependency_path_str[:len(JOINPOINT)] == JOINPOINT
    elif ent_number == 2:
        return dependency_path_str[-len(JOINPOINT):] == JOINPOINT
    else:
        raise ValueError('ent_number should be 1 or 2')

def get_dependecy_path_str(ent1, ent2):
    ent1_to_root, ent2_to_root, join_point = get_dependency_path_arr(ent1, ent2)
    path = ""
    for w in ent1_to_root:
        path += w.dep_ + "<-"
    if join_point != None:
        path += JOINPOINT
    else:
        path += SPLIT_ROOTS

    for j in range(len(ent2_to_root)-1,-1 , -1):
        path += "->" + ent2_to_root[j].dep_

    # print ("sentence: " + ent1[ENT_OBJ_ROOT].doc.text)
    # print ("ent1: " + ent1[ENT_OBJ_ROOT].text)
    # print ("ent2: " + ent2[ENT_OBJ_ROOT].text)
    # print(" path: " + path)

    return path

def get_dependecy_path_pos_str(ent1, ent2):
    ent1_to_root, ent2_to_root, join_point = get_dependency_path_arr(ent1, ent2)
    path = ""
    for w in ent1_to_root:
        path += w.pos_ + "<-"
    if join_point != None:
        path += join_point.pos_
    else:
        path += SPLIT_ROOTS

    for j in range(len(ent2_to_root)-1,-1 , -1):
        path += "->" + ent2_to_root[j].pos_
    return path


def get_dependency_path_arr(ent1, ent2):
    ent1_root = ent1[ENT_OBJ_ROOT]
    ent2_root = ent2[ENT_OBJ_ROOT]
    curr = ent1_root
    ent1_to_root = []
    i_from_ent1 = {}
    while curr.dep_ != "ROOT":
        i_from_ent1[curr.i] = len(ent1_to_root)
        ent1_to_root.append(curr)
        curr = curr.head
    ent1_to_root.append(curr)

    ent2_to_root = []
    curr = ent2_root
    joining_point_id = -1
    while curr.dep_!="ROOT":
        if curr.i in i_from_ent1:
            joining_point_id = curr.i
            break
        ent2_to_root.append(curr)
        curr = curr.head
    if joining_point_id == -1:
        ent2_to_root.append(curr)

    ent1_path = []
    join_point = None
    if joining_point_id != -1:
        stop = i_from_ent1[joining_point_id]
        for i in range(stop):
            ent1_path.append(ent1_to_root[i])
        join_point = ent1_to_root[stop]
    else:
        ent1_path = ent1_to_root

    return ent1_path, ent2_to_root, join_point


def get_dist(ent1, ent2):
    ent1_i = ent1[ENT_OBJ_ROOT].i
    ent2_i = ent2[ENT_OBJ_ROOT].i
    return abs(ent1_i - ent2_i)