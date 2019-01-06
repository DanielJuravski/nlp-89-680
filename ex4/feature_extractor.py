from sklearn.feature_extraction import DictVectorizer, FeatureHasher
import spacy_parser as parser
from spacy_parser import ENT_OBJ_SPACY_ENT, ENT_OBJ_LABEL, ENT_OBJ_TEXT, ENT_OBJ_ROOT
from Lexicon_helper import Lexicon_helper

ROW_ID_INDEX = 0
HEAD_INDEX = 5
NER_TYPE_INDEX = 8
WORD_FORM_INDEX = 1


class FeatureExtractor:
    def __init__(self, fh=None, fs=None):
        if fh:
            self.feature_hasher = fh
        if fs:
            self.features_set = fs
            self.train_mode = False
        else:
            self.features_set = set()

        self.lexicon_helper = Lexicon_helper()

    features_set = None
    feature_hasher = None
    train_mode = True
    unk = "unk"

    def build_x_vectors(self,  ent_couple_objects):
        '''

        :param tuple(sen_id, ent1 name, ent2 name, x)
        :return: tuple(sen_id, ent1 name, ent2 name, x)
        '''
        if not self.feature_hasher:
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
        features = []
        sen_id = ent_tuple[0]
        ent1_text = self.extract_text(ent_tuple[1])
        ent2_text = self.extract_text(ent_tuple[2])

        #Entity features
        ent1_type = self.extract_type(ent_tuple[1])
        ent2_type = self.extract_type(ent_tuple[2])
        ent1_head = self.extract_head(ent_tuple[1])
        ent2_head = self.extract_head(ent_tuple[2])
        concatenated_types = ent1_type + ent2_type
        features.append(self.get_feature("e1_type", ent1_type))
        features.append(self.get_feature("e2_type", ent2_type))
        features.append(self.get_feature("e1_head", ent1_head))
        features.append(self.get_feature("e2_head", ent2_head))
        features.append(self.get_feature("concanated_types", concatenated_types))

        #Lexicon Features
        features.append(self.get_feature("e1_lex_fname", self.lexicon_helper.does_include_first_name(ent1_text)))
        features.append(self.get_feature("e1_lex_lname", self.lexicon_helper.does_include_last_name(ent1_text)))
        features.append(self.get_feature("e2_lex_loc", self.lexicon_helper.is_location(ent2_text)))

        #word based features
        words_between_ents = parser.get_words_between(ent_tuple[1], ent_tuple[2])
        for word in words_between_ents:
            features.append(self.get_feature("bow", word))

        features.append(self.get_feature("ent1_bword", ent_tuple[1][ENT_OBJ_ROOT].left_edge.text))
        features.append(self.get_feature("ent2_aword", ent_tuple[2][ENT_OBJ_ROOT].right_edge.text))

        #syntactic features
        dependency_path_str = parser.get_dependency_path(ent_tuple[1], ent_tuple[2])
        features.append((self.get_feature("dep_path", dependency_path_str)))


        e1_clean = self.clean_name(ent1_text)
        e2_clean = self.clean_name(ent2_text)
        return (sen_id, e1_clean, e2_clean, features)

    def extract_text(self, ent_obj):
        return ent_obj[ENT_OBJ_TEXT]

    def extract_type(self, ent_obj):
        return ent_obj[ENT_OBJ_LABEL]


    def extract_head(self, ent_obj):
        return ent_obj[ENT_OBJ_ROOT].head.lemma_


    def clean_name(self, name):
        return name

    def get_feature(self, feature_prefix, feature_val):
        feature = feature_prefix+str(feature_val)
        if self.train_mode:
            self.features_set.add(feature)
            self.features_set.add(feature_prefix + self.unk)
            return feature
        else:
            if feature in self.features_set:
                return feature
            else:
                return feature_prefix + self.unk



