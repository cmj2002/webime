"""
Author: Cao Ming jun
Date: 2022-07-12
Description: Creating start vector, transition probability matrix and emission probability matrix.
"""

from backend.utils import *
from math import log
from pypinyin import pinyin as get_pinyin
from pypinyin import NORMAL


def gen_start():
    """
    Generate start vector and save.
    :return: None
    """
    counter = {}
    total = 0
    for word, freq in tqdm(read_data(), desc='Counting start vector'):
        counter[word[0]] = counter.get(word[0], 0) + freq
        total += freq
    start_vector = {}
    for key, value in counter.items():
        start_vector[key] = log(value / total)
    save_json(start_vector, START_VECTOR_FILE)


def gen_transition():
    """
    Generate transition probability matrix and save.
    :return: None
    """
    counter = {}
    for word, freq in tqdm(read_data(), desc='Counting transition matrix'):
        for i in range(len(word) - 1):
            if word[i] in counter:
                counter[word[i]][word[i + 1]] = counter[word[i]].get(word[i + 1], 0) + freq
            else:
                counter[word[i]] = {word[i + 1]: freq}
    transition_matrix = {}
    for first, char_map in counter.items():
        transition_matrix[first] = {}
        total = sum(char_map.values())
        for second, value in char_map.items():
            transition_matrix[first][second] = log(value / total)
    save_json(transition_matrix, TRANSITION_MATRIX_FILE)


def gen_emission():
    """
    Generate emission probability matrix and save.
    :return: None
    """
    counter = {}
    for word, freq in tqdm(read_data(), desc='Counting emission matrix'):
        pinyin = get_pinyin(word, style=NORMAL)
        for ch, heteronyms in zip(word, pinyin):
            if ch not in counter:
                counter[ch] = {}
            for py in heteronyms:
                py = normalize(py)

                # manage total_prior
                if len(py) == 1:
                    total_prior = 1
                elif len(py) == 2:
                    total_prior = 1 + COMMON_INCOMPLETE_DEGRADE
                elif len(py) >= 3:
                    total_prior = 1 + INCOMPLETE_DEGRADE * (len(py) - 2) + COMMON_INCOMPLETE_DEGRADE
                else:
                    raise ValueError('Pinyin length error: {}'.format(py))

                k = freq / (len(heteronyms) * total_prior)
                if len(py) >= 1:
                    counter[ch][py] = counter[ch].get(py, 0) + k
                if len(py) >= 2:
                    counter[ch][py[0]] = counter[ch].get(py[0], 0) + k * COMMON_INCOMPLETE_DEGRADE
                if len(py) >= 3:
                    for i in range(2, len(py)):
                        counter[ch][py[:i]] = counter[ch].get(py[:i], 0) + k * INCOMPLETE_DEGRADE
    emission_matrix = {}
    for ch, py_map in counter.items():
        emission_matrix[ch] = {}
        total = sum(py_map.values())
        for py, value in py_map.items():
            emission_matrix[ch][py] = log(value / total)
    save_json(emission_matrix, EMISSION_MATRIX_FILE)


def gen_reverse_emission():
    """
    Generate reverse emission probability matrix and save.
    :return: None
    """
    emission_matrix = load_json(EMISSION_MATRIX_FILE)
    reverse_emission = {}
    for ch, py_map in tqdm(emission_matrix.items(), desc='Generating reverse emission matrix'):
        for py, value in py_map.items():
            if py not in reverse_emission:
                reverse_emission[py] = {}
            reverse_emission[py][ch] = value
    save_json(reverse_emission, REVERSE_EMISSION_FILE)


def gen_united_reverse():
    """
    Generate united reverse probability matrix and save.
    :return: None
    """
    emission_matrix = load_json(EMISSION_MATRIX_FILE)
    transition_matrix = load_json(TRANSITION_MATRIX_FILE)
    united_reverse = {}
    for first, char_map in tqdm(transition_matrix.items(), desc='Generating united reverse matrix'):
        united_reverse[first] = {}
        for second, p1 in char_map.items():
            for py, p2 in emission_matrix[second].items():
                prob = p1 + p2
                if py not in united_reverse[first]:
                    united_reverse[first][py] = [second, prob]
                elif prob > united_reverse[first][py][1]:
                    united_reverse[first][py] = [second, prob]
    save_json(united_reverse, UNITED_REVERSE_FILE)

def train():
    gen_start()
    gen_transition()
    gen_emission()
    gen_reverse_emission()
    gen_united_reverse()

if __name__ == '__main__':
    train()
