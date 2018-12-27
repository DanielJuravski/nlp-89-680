TEXT_PREFIX = "#text:"
PROCESSED_LINE_NER_BIO = 7
ID_LINE_PREF = "#id: "

def load_processed_sentences(processed_file):
    parsed_sentences = {}
    raw_sentences = {}
    with open(processed_file) as f:
        content = f.readlines()
        sent_id = ""
        for line in content:
            line_arr = line.split()
            if not line_arr:
                continue
            elif line[:len(ID_LINE_PREF)] == ID_LINE_PREF:
                sent_id = line[len(ID_LINE_PREF):].strip()
                parsed_sentences[sent_id] = []
            elif TEXT_PREFIX in line_arr[0]:
                raw_sentences[sent_id] = line[len(TEXT_PREFIX):].strip()
            else:
                parsed_sentences[sent_id].append(line_arr)

    return parsed_sentences, raw_sentences


def get_xs_from_sen(sen_id, sentence):
    """

    :param sen_id:
    :param sentence:
    :return array of tuples (sen_id, ent1, ent2):
    """
    xs = []
    entities = []
    curr_entity = []
    for line in sentence:
        if line[PROCESSED_LINE_NER_BIO] == 'B' and len(curr_entity) > 0:
            entities.append(curr_entity)
            curr_entity = []
        elif line[PROCESSED_LINE_NER_BIO] != 'O':
           curr_entity.append(line)
        else:
            if len(curr_entity) > 0:
                entities.append(curr_entity)
                curr_entity = []

    if len(curr_entity) > 0:
        entities.append(curr_entity)

    for i, ent_i in enumerate(entities):
        for j, ent_j in enumerate(entities):
            if i != j:
                xs.append((sen_id, ent_i, ent_j))

    return xs


def get_x_data(feature_extractor, processed_sentences):
    all_x_ent_tuples_data = []
    for sen_id in processed_sentences:
        sentence_x_data = get_xs_from_sen(sen_id,processed_sentences[sen_id])
        all_x_ent_tuples_data += sentence_x_data

    all_x_data = []
    for ent_tuple in all_x_ent_tuples_data:
        extracted_x = feature_extractor.extract_features(ent_tuple, processed_sentences[ent_tuple[0]])
        all_x_data.append(extracted_x)

    sen_entities, x_data = feature_extractor.build_x_vectors(all_x_data)
    return sen_entities


LIVE_IN = "Live_In"