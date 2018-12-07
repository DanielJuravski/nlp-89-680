import sys

TAG_PREFIX = "_tag:"

FEATURE_PREFIX = "_feature:"

WORD_PREFIX = "_word:"

tagset_map = {}
feat_map = {}
word_to_tags = {}


def extract_features(file):
    last_tag_value = 1
    last_feat_value = 1
    mat = []
    with open(file) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        for line in content:
            arr = line.split()

            # taking care of the tag
            this_tag = arr[0]
            if tagset_map.has_key(this_tag):
                tag_val = tagset_map[this_tag]
            else:
                tagset_map[this_tag] = last_tag_value
                tag_val = last_tag_value
                last_tag_value += 1

            # taking care of the features
            feat_val_arr = []
            for i in range(1, len(arr)):
                this_feat = arr[i]
                if feat_map.has_key(this_feat):
                    feat_val = feat_map[this_feat]
                else:
                    feat_map[this_feat] = last_feat_value
                    feat_val = last_feat_value
                    last_feat_value += 1
                feat_val_arr.append(feat_val)
                if "form=" in this_feat:
                    word = this_feat[5:]
                    if word not in word_to_tags:
                        word_to_tags[word] = set()
                    word_to_tags[word].add(this_tag)

            feat_val_arr.sort()
            mat.append([tag_val, feat_val_arr])
    return mat


def write_to_vec_file(file, mat):
    with open(file, 'w') as f:
        for i in range(len(mat)):
            f.write("%s" % mat[i][0])
            for k in range(len(mat[i][1])):
                f.write(" %s:1" % mat[i][1][k])
            f.write("\n")



def write_maps(file):
    with open(file, 'w') as f:
        for k, v in tagset_map.items():
            f.write(TAG_PREFIX + str(k) + " " + str(v) + "\n")
        for k, v in feat_map.items():
            f.write(FEATURE_PREFIX + str(k) + " " + str(v) + "\n")
        for w in word_to_tags:
            for tag in word_to_tags[w]:
                f.write(WORD_PREFIX + str(w) + " " + str(tag) + "\n")


if __name__ == '__main__':
    features_file = sys.argv[1]
    feature_vecs_file = sys.argv[2]
    feature_map_file = sys.argv[3]


    mat = extract_features(features_file)
    write_to_vec_file(feature_vecs_file, mat)
    write_maps(feature_map_file)

    print(feature_vecs_file + " was created")
    print(feature_map_file + " was created")
