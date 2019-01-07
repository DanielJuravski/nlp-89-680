
PATH_FOR_FIRST_NAMES_LEXICON = "extra_data/lexicon/firstname.5k"

PATH_FOR_LAST_NAMES_LEXICON = "extra_data/lexicon/lastname.5000"
PATH_FOR_PEOPLE_FAMILYNAME_LEXICON = "extra_data/lexicon/people.family_name"
PATH_FOR_PEOPLE_PERSON_LASTNAME_LEXICON = "extra_data/lexicon/people.person.lastnames"

PATH_FOR_LOCATION_LEXICON = "extra_data/lexicon/location"
PATH_FOR_LOCATION_COUNTRY_LEXICON = "extra_data/lexicon/location.country"


class Lexicon_helper:
    def __init__(self):
        self.first_names_set = set()
        self.last_names_set = set()
        self.locations_set = set()
        self.load_lexicons()

    def load_lexicons(self):
        with open(PATH_FOR_FIRST_NAMES_LEXICON) as f:
            for line in f.readlines():
                self.first_names_set.add(line.strip())

        with open(PATH_FOR_LAST_NAMES_LEXICON) as f:
            for line in f.readlines():
                self.last_names_set.add(line.strip())
        with open(PATH_FOR_PEOPLE_FAMILYNAME_LEXICON) as f:
            for line in f.readlines():
                self.last_names_set.add(line.strip())
        with open(PATH_FOR_PEOPLE_PERSON_LASTNAME_LEXICON) as f:
            for line in f.readlines():
                self.last_names_set.add(line.strip())

        with open(PATH_FOR_LOCATION_LEXICON) as f:
            for line in f.readlines():
                self.locations_set.add(line.strip())
        with open(PATH_FOR_LOCATION_COUNTRY_LEXICON) as f:
            for line in f.readlines():
                self.locations_set.add(line.strip())

    def does_include_first_name(self, entitiy_text):
        for word in entitiy_text.split():
            if word.upper() in self.first_names_set:
                return True
        return False

    def does_include_last_name(self, entitiy_text):
        for word in entitiy_text.split():
            if word in self.last_names_set:
                return True
        return False

    def is_location(self, entity_text):
        return entity_text in self.locations_set