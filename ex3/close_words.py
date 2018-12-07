import io
import numpy as np
from prettytable import PrettyTable


TARGET_WORDS = ["car", "bus", "hospital", "hotel", "gun", "bomb", "horse", "fox", "table", "bowl", "guitar", "piano"]


def get_close_words(words_matrix, context_matrix, num):
    W, words = words_matrix
    contextW, context_titles = context_matrix
    results = {}
    w2i = {w:i for i, w in enumerate(words)}
    for target_word in TARGET_WORDS:
        v = W[w2i[target_word]]
        dot_products = contextW.dot(v)
        most_similar_ids = dot_products.argsort()[-1:-(num+1):-1]
        similar_results = context_titles[most_similar_ids]
        results[target_word] = similar_results

    return results


def load_vectors(file_path):
    words = []
    vectors = []
    counter = 0
    with open(file_path) as f:
        content = f.readlines()
        for line in content:
            line_arr = line.split()
            word = line_arr[0]
            vector = np.array([float(x) for x in line_arr[1:]])
            vector = vector/np.linalg.norm(vector)
            # words = np.append(words, word)
            # vectors = np.append(vectors, vector)
            words.append(word)
            vectors.append(vector)
            counter += 1
            if counter % 1000 == 0:
                print("loaded line num %d" % counter)

    return np.array(vectors), np.array(words)


def print_tables(results_dicts_arr, out_path, rows_amount):
    f = io.open(out_path, 'w', encoding='utf8')
    headers=["word\\type"] + [x[0] for x in results_dicts_arr]
    t = PrettyTable(headers)
    for w in TARGET_WORDS:
        t.add_row(["---"] + ["---" for x in results_dicts_arr])
        t.add_row([w] + [x[1][w][0] for x in results_dicts_arr])
        for i in range(1, rows_amount):
            t.add_row([""] + [x[1][w][i] for x in results_dicts_arr])

    f.write(t.get_string())





if __name__ == '__main__':
    bow5_words_vectors, bow5_words_titles = load_vectors("data/bow5.words")
    close_words_bow5 = get_close_words((bow5_words_vectors, bow5_words_titles),
                                       (bow5_words_vectors, bow5_words_titles), 20)

    dep_words_vectors, dep_words_titles = load_vectors("data/deps.words")
    close_words_deps = get_close_words((dep_words_vectors, dep_words_titles),
                                       (dep_words_vectors, dep_words_titles), 20)

    dicts = [("bow5", close_words_bow5), ("dep", close_words_deps)]
    print_tables(dicts, "word2vec_closets_words", 20)

    bow5_context_vectors, bow5_context_titles = load_vectors("data/bow5.contexts")
    contexts_bow5 = get_close_words((bow5_words_vectors, bow5_words_titles),
                                    (bow5_context_vectors, bow5_context_titles), 10)
    dep_context_vectors, dep_context_titles = load_vectors("data/deps.contexts")
    contexts_deps = get_close_words((dep_words_vectors, dep_words_titles),
                                    (dep_context_vectors, dep_context_titles), 10)
    dicts_contexts = [("bow5-contexts", contexts_bow5), ("dep-contexts", contexts_deps)]
    print_tables(dicts_contexts, "word2vec_strongest_contexts", 10)




