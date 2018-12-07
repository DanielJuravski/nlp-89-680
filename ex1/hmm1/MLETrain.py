import sys


#Initntalize 3 dictionaries of type {tag: count} {(tag, prev tag):count} {(tag, prev tag, second prev tag):count}
def get_q_dict(file_name):
    with open(file_name) as f:
        content=f.readlines()

    q_singles = {}
    q_doubles = {}
    q_triples = {}
    content=[x.strip() for x in content]
    for line in content:
        pairs = line.split(" ")
        tags = []
        for pair in pairs:
            tags.append(pair.rsplit("/",1)[1])
        # for initializing with 'start' tags, as result runs once at a sentence
        if q_singles.has_key('start'):
            q_singles['start'] += 1
        else:
            q_singles['start'] = 1

        if q_doubles.has_key(('start', 'start')):
            q_doubles[('start', 'start')] += 1
        else:
            q_doubles[('start', 'start')] = 1

        for i in range(len(tags)):
            if i ==0:
                prev = 'start'
                second_prev = 'start'
            elif i == 1:
                prev = tags[i-1]
                second_prev = 'start'
            else:
                prev = tags[i-1]
                second_prev = tags[i-2]

            if q_singles.has_key(tags[i]):
                q_singles[tags[i]] +=1
            else:
                q_singles[tags[i]] = 1

            if q_doubles.has_key((prev, tags[i])):
                q_doubles[(prev, tags[i])] +=1
            else:
                q_doubles[(prev, tags[i])] = 1

            if q_triples.has_key((second_prev, prev, tags[i])):
                q_triples[(second_prev, prev, tags[i])] +=1
            else:
                q_triples[(second_prev, prev, tags[i])] = 1

    return (q_singles, q_doubles, q_triples)


#Initntalize a dictionary of type {(word,tag): count}
def get_e_dict(file_name):
    with open(file_name) as f:
        content=f.readlines()

    e_dict = {}
    content=[x.strip() for x in content]
    for line in content:
        pairs = line.split(" ")
        for pair in pairs:
            arr = pair.rsplit("/",1)
            word = arr[0]
            tag = arr[1]
            if e_dict.has_key((word,tag)):
                e_dict[(word,tag)] +=1
            else:
                e_dict[(word,tag)] = 1
    return e_dict


#append unk to dict
def append_unk_to_dict():
    unk_dict = {}
    for (word,tag) in e_dict:
        if e_dict[(word, tag)] == 1:
            if word.endswith("s"):
                continue
            elif unk_dict.has_key(('unk', tag)):
                unk_dict[('unk', tag)] += 1
            else:
                unk_dict[('unk', tag)] = 1

    for (word, tag) in unk_dict:
        e_dict[(word, tag)] = unk_dict[(word, tag)]


# append ^_ing to dict
def append_ing_to_dict():
    ing_dict = {}
    for (word, tag) in e_dict:
        if word.endswith('ing'):
            amount = e_dict[(word, tag)]
            if ing_dict.has_key(('^_ing', tag)):
                ing_dict[('^_ing', tag)] += amount
            else:
                ing_dict[('^_ing', tag)] = amount

    for (word, tag) in ing_dict:
        e_dict[(word, tag)] = ing_dict[(word, tag)]


# append ^_ed to dict
def append_ed_to_dict():
    ed_dict = {}
    for (word, tag) in e_dict:
        if word.endswith('ed'):
            amount = e_dict[(word, tag)]
            if ed_dict.has_key(('^_ed', tag)):
                ed_dict[('^_ed', tag)] += amount
            else:
                ed_dict[('^_ed', tag)] = amount

    for (word, tag) in ed_dict:
        e_dict[(word, tag)] = ed_dict[(word, tag)]



# append ^_s to dict
def append_s_to_dict():
    s_dict = {}
    for (word, tag) in e_dict:
        if word.endswith('s'):
            amount = e_dict[(word, tag)]
            if s_dict.has_key(('^_s', tag)):
                s_dict[('^_s', tag)] += amount
            else:
                s_dict[('^_s', tag)] = amount

    for (word, tag) in s_dict:
        e_dict[(word, tag)] = s_dict[(word, tag)]

# append firstuppercase to dict
def append_UC_to_dict():
    uc_dict = {}
    for (word, tag) in e_dict:
        if word[0].isupper():
            amount = e_dict[(word, tag)]
            if uc_dict.has_key(('^A_', tag)):
                uc_dict[('^A_', tag)] += amount
            else:
                uc_dict[('^A_', tag)] = amount

    for (word, tag) in uc_dict:
        e_dict[(word, tag)] = uc_dict[(word, tag)]


# append alluppercase to dict
def append_allUC_to_dict():
    alluc_dict = {}
    for (word, tag) in e_dict:
        for i in range(len(word)):
            if word[i].isalpha() and word[i].isupper():
                amount = e_dict[(word, tag)]
                if alluc_dict.has_key(('^ABC', tag)):
                    alluc_dict[('^ABC', tag)] += amount
                else:
                    alluc_dict[('^ABC', tag)] = amount

    for (word, tag) in alluc_dict:
        e_dict[(word, tag)] = alluc_dict[(word, tag)]


if __name__ == '__main__':
    input_file_name = sys.argv[1]
    q_mle_filename = sys.argv[2]
    e_mle_filename = sys.argv[3]
    print("input file= " + repr(input_file_name))
    print("q file= " + repr(q_mle_filename))
    print("e file=  " + repr(e_mle_filename))
    e_dict = get_e_dict(input_file_name)
    append_unk_to_dict()
    append_ing_to_dict()
    append_ed_to_dict()
    append_UC_to_dict()
    append_allUC_to_dict()
    append_s_to_dict()
    output = open(e_mle_filename, 'w')
    for key, value in e_dict.iteritems():
        output.write("%s %s\t%d\n" % (key[0], key[1], value))
    output.close()

    q_singles, q_doubles, q_triples = get_q_dict(input_file_name)
    output = open(q_mle_filename, 'w')
    for key, value in q_singles.iteritems():
        output.write("%s\t%d\n" % (key, value))
    for key, value in q_doubles.iteritems():
        output.write("%s %s\t%d\n" % (key[0], key[1], value))
    for key, value in q_triples.iteritems():
        output.write("%s %s %s\t%d\n" % (key[0], key[1], key[2], value))
    output.close()


