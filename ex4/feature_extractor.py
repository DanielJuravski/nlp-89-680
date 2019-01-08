from sklearn.feature_extraction import DictVectorizer, FeatureHasher
import spacy_parser as parser
from spacy_parser import ENT_OBJ_SPACY_ENT, ENT_OBJ_LABEL, ENT_OBJ_TEXT, ENT_OBJ_ROOT
from Lexicon_helper import Lexicon_helper

ROW_ID_INDEX = 0
HEAD_INDEX = 5
NER_TYPE_INDEX = 8
WORD_FORM_INDEX = 1


class FeatureExtractor:
    def __init__(self, lexicon_helper, fh=None, fs=None):
        if fh:
            self.feature_hasher = fh
        if fs:
            self.features_set = fs
            self.train_mode = False
        else:
            self.features_set = set()

        self.lexicon_helper = lexicon_helper

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
        features.append(self.get_feature("e1_root", ent_tuple[1][ENT_OBJ_ROOT].lemma_))
        features.append(self.get_feature("e2_root", ent_tuple[2][ENT_OBJ_ROOT].lemma_))
        features.append(self.get_feature("concanated_types", concatenated_types))

        #Lexicon Features
        features.append(self.get_feature("e1_lex_fname", self.lexicon_helper.does_include_first_name(ent1_text)))
        features.append(self.get_feature("e1_lex_lname", self.lexicon_helper.does_include_last_name(ent1_text)))
        features.append(self.get_feature("e2_lex_loc", self.lexicon_helper.is_location(ent2_text)))

        #word based features
        words_between_ents = parser.get_words_between(ent_tuple[1], ent_tuple[2])
        for word in words_between_ents:
            features.append(self.get_feature("bow", word.text))

        features.append(self.get_feature("ent1_bword", ent_tuple[1][ENT_OBJ_ROOT].left_edge.text))
        features.append(self.get_feature("ent2_aword", ent_tuple[2][ENT_OBJ_ROOT].right_edge.text))



        #syntactic features
        features.append(self.get_feature("ent_dist", parser.get_dist(ent_tuple[1], ent_tuple[2])))
        dependency_path_str = parser.get_dependecy_path_str(ent_tuple[1], ent_tuple[2])
        features.append(self.get_feature("dep_path", dependency_path_str))
        dependency_path_pos_str = parser.get_dependecy_path_pos_str(ent_tuple[1], ent_tuple[2])
        features.append(self.get_feature("dep_pos_path", dependency_path_pos_str))

        #features that decrement f1 but could be used for rules

        features.append(self.get_feature("is_descriptive_path", parser.is_descriptive_path(ent_tuple[1], ent_tuple[2])))
        #
        #ent1_to_root, ent2_to_root, joinpoint = parser.get_dependency_path_arr(ent_tuple[1], ent_tuple[2])
        # for i, w in enumerate(ent1_to_root):
        #     features.append(self.get_feature("e1_2root_pos_"+str(i), w.lemma_))
        # for i, w in enumerate(ent2_to_root):
        #     features.append(self.get_feature("e2_2root_pos_"+str(i), w.lemma_))
        # if joinpoint != None:
        #     features.append(self.get_feature("joinpoint_pos", joinpoint.pos_))
        #
        # features.append(self.get_feature("len_en1toroot", len(ent1_to_root)))
        # features.append(self.get_feature("len_en2toroot", len(ent2_to_root)))

        #
        # features.append(self.get_feature("split_roots", parser.is_split_roots(dependency_path_str)))
        # features.append(self.get_feature("ent1_ancestor", parser.is_anccestor(dependency_path_str, 1)))
        # features.append(self.get_feature("ent2_ancestor", parser.is_anccestor(dependency_path_str, 2)))
        #

        e1_clean = self.clean_name(ent_tuple[1])
        e2_clean = self.clean_name(ent_tuple[2])
        return (sen_id, e1_clean, e2_clean, features)

    def extract_text(self, ent_obj):
        return parser.clean_entity_text(ent_obj[ENT_OBJ_TEXT], ent_obj[ENT_OBJ_ROOT])

    def extract_type(self, ent_obj):
        return ent_obj[ENT_OBJ_LABEL]


    def extract_head(self, ent_obj):
        return ent_obj[ENT_OBJ_ROOT].head.lemma_

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

    def clean_name(self, ent_obj):
        return parser.modify_entity_text(ent_obj[ENT_OBJ_TEXT], ent_obj[ENT_OBJ_SPACY_ENT])



