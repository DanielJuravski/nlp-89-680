from sklearn.feature_extraction import DictVectorizer, FeatureHasher

ROW_ID_INDEX = 0
HEAD_INDEX = 5
NER_TYPE_INDEX = 8
WORD_FORM_INDEX = 1


class FeatureExtractor:

    features_set = set()
    feature_hasher = None

    def build_x_vectors(self,  ent_couple_objects):
        '''

        :param tuple(sen_id, ent1 name, ent2 name, x)
        :return: tuple(sen_id, ent1 name, ent2 name, x)
        '''

        self.feature_hasher = FeatureHasher(n_features=len(self.features_set), input_type='string')
        x_data = self.feature_hasher.transform([t[3] for t in ent_couple_objects])
        converted_ent_objects = [(t[0], t[1], t[2], x_data[i]) for i,t in enumerate(ent_couple_objects)]
        return converted_ent_objects, x_data


    def extract_features(self, ent_tuple, sentence):
        '''

        :param ent_tuple:
        :param sentence:
        :return: tuple(sen_id, ent1 name, ent2 name, x)
        '''

        sen_id = ent_tuple[0]
        ent1_name = self.extract_name(ent_tuple[1])
        ent2_name = self.extract_name(ent_tuple[2])

        ent1_type = self.extract_type(ent_tuple[1])
        ent2_type = self.extract_type(ent_tuple[2])
        ent1_head = self.extract_head(ent_tuple[1])
        ent2_head = self.extract_head(ent_tuple[2])
        concatenated_types = ent1_type + ent2_type

        features = []
        features.append(self.add_feature_and_return("e1_type" + ent1_type))
        features.append(self.add_feature_and_return("e2_type" + ent2_type))
        features.append(self.add_feature_and_return("e1_head" + ent1_head))
        features.append(self.add_feature_and_return("e2_head" + ent2_head))

        e1_clean = self.clean_name(ent1_name)
        e2_clean = self.clean_name(ent2_name)
        return (sen_id, e1_clean, e2_clean, features)

    def extract_name(self, ent_lines_arr):
        name = ""
        for line in ent_lines_arr:
            name += line[WORD_FORM_INDEX] + " "

        return name.strip()

    def extract_type(self, ent_lines_arr):
        return ent_lines_arr[0][NER_TYPE_INDEX]


    def extract_head(self, ent_lines_arr):
        head = ent_lines_arr[0][HEAD_INDEX]
        found_head = False
        ent_line_i = 0
        while not found_head:
            found_head = True
            for i, line in enumerate(ent_lines_arr):
                if head == line[ROW_ID_INDEX]:
                    head = line[HEAD_INDEX]
                    ent_line_i = i
                    found_head = False

        return ent_lines_arr[ent_line_i][WORD_FORM_INDEX]


    def clean_name(self, name):
        return name

    def add_feature_and_return(self, feature):
        self.features_set.add(feature)
        return feature



