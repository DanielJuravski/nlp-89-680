import sys
import utils


def extract_by_NER(sen):
    relations = []
    persons = []
    geos = []

    for ent in sen.doc.ents:
        if ent.label_ == 'PERSON':
            persons.append((ent.text, ent))
        elif ent.label_ == 'GPE':
            geos.append((ent.text, ent))

    persons = filter_persons_by_compnoun(persons, sen)

    for person in persons:
        for geo in geos:
            relations.append((person, geo))


    return relations


def filter_persons_by_compnoun(persons, sen):
    for token in sen.doc:
        # print(token.text, token.dep_, token.head.text, token.head.pos_, [child for child in token.children])
        if token.dep_ == 'compound' and token.head.pos_ == 'NOUN':
            for p in persons:
                if p[0] == token.text:
                    persons.remove(p)
    return persons


def check_pos_in_children(head, uphill_child, geo_entity):
    if head == geo_entity.root:
        return True

    found = False
    for child in head.children:
        if child != uphill_child:
            found = found or check_pos_in_children(child, uphill_child, geo_entity)

    return found


def filter_by_dep_tree_via_verb(sen_relations, sen):
    filtered = []
    found = False
    for relation in sen_relations:
        per_entity = relation[0][1]
        geo_entity = relation[1][1]
        head = per_entity.root.head
        uphill_child = per_entity.root
        print(head.text)
        while uphill_child != head:
            print ("###head###")
            print(head.text)
            if head.pos_ == 'VERB':
                found = found or check_pos_in_children(head, uphill_child, geo_entity)
            print ("###children###")
            for child in head.children:
                print child.text

            uphill_child = head
            head = head.head


        if found:
            filtered.append(relation)

    return filtered


def extract_from_sentences(data):
    relations = {}
    sorted_sen_ids = utils.get_sorted_ids(data.keys())
    for sen_id in sorted_sen_ids:
        sen = data[sen_id]
        sen_relations = extract_by_NER(sen)
        sen_relations = filter_by_dep_tree_via_verb(sen_relations, sen)
        if len(sen_relations) > 0:
            print sen_id
            for token in sen.doc:
                print(token.text, token.dep_, token.head.text, token.head.pos_, [child for child in token.children])
        relations[sen_id] = [(r[0][0], r[1][0]) for r in sen_relations]

    return relations




if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    data = {}
    for sen_id, sen in utils.read_lines(sys.argv[1]):
        data[sen_id] = utils.nlp(sen)
    relations = extract_from_sentences(data)
    utils.print_relations(relations, data, output_file)