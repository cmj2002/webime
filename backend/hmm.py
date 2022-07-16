from backend.utils import *
from backend.classes import Answer
import heapq

# load data
start_vector = load_json(START_VECTOR_FILE)
reverse_emission_matrix = load_json(REVERSE_EMISSION_FILE)
united_reverse_matrix = load_json(UNITED_REVERSE_FILE)


def viterbi(raw_answer: Answer, width: int) -> List[Answer]:
    """
    Viterbi algorithm.
    :param raw_answer: an instance of Answer that is not calculated by HMM.
    :param width: the maximum number of answers to be returned.
    :return: a list of answers.
    """
    pinyin = raw_answer.partition
    candidate_init_chars = ((ch, start_vector[ch] + reverse_emission_matrix[pinyin[0]][ch]) for ch in
                            reverse_emission_matrix[pinyin[0]])
    raw_results = {ch: prob for ch, prob in heapq.nlargest(
        width, candidate_init_chars, key=lambda x: x[1])}
    stop_point = sum([len(s) for s in pinyin])
    for i in range(1, len(pinyin)):
        py = pinyin[i]
        next_result = {}
        for phrase, prob in raw_results.items():
            first = phrase[-1]
            if first in united_reverse_matrix and py in united_reverse_matrix[first]:
                state, new_prob = united_reverse_matrix[first][py]
                next_result[phrase + state] = new_prob + prob
        if next_result:
            raw_results = next_result
        else:
            # no result found
            stop_point = sum([len(p) for p in pinyin[:i]])
            break
    return [raw_answer.set_answer(answer, prob, stop_point) for answer, prob in raw_results.items()]


if __name__ == '__main__':
    out = viterbi(Answer(['ni', 'hao', 'shi', 'jie', 'nan', 'jing', 'da', 'xue', 'cao', 'ming', 'jun'], 1.0), width=20)
    print(json.dumps(viterbi(Answer(['ni', 'hao', 'shi', 'jie'], 1.0), width=20),
                     indent=4, default=str, ensure_ascii=False))
    print(json.dumps(viterbi(Answer(['nan', 'jing', 'da', 'xue'], 1.0), width=20),
                     indent=4, default=str, ensure_ascii=False))
