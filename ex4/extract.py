import sys

import utils


def extract_by_NER(data):
    for sen_id in data:
        sen = data[sen_id]
        print sen_id
        print sen.text


if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    data = {}
    for sen_id, sen in utils.read_lines(sys.argv[1]):
        data[sen_id] = sen
    relations = extract_by_NER(data)
