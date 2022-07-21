from backend.classes import Answer
from backend.cut import cut
from backend.hmm import viterbi
from functools import lru_cache
from backend.utils import *
import time


def merge(pinyin: str, common_answers: List[Answer], error_answers: List[Answer]) -> List[Answer]:
    """
    Merge common answers and error answers by adding error correction that is not in common answers.
    Error answers are degraded and not allow to be the first answer.
    If not common answers, the first one will be raw pinyin.
    :param pinyin: raw pinyin in case we need it.
    :param answers: set of Answer instances.
    :return: set of Answer instances.
    """

    def in_list(_answer: Answer, _answers: List[Answer]) -> Optional[int]:
        assert _answer.answer is not None
        for i in range(len(_answers)):
            if _answers[i].answer == _answer.answer:
                return i
        return None

    if len(common_answers) == 0:
        simpleAnswer=Answer([pinyin], 1.0)
        simpleAnswer.answer=pinyin
        simpleAnswer.probability=0.0
        simpleAnswer.process_to=len(pinyin)
        common_answers.append(simpleAnswer)
    common_answers.sort(key=lambda x: x.get_prob(), reverse=True)
    first = common_answers[0]
    _res = common_answers[1:] + error_answers
    res = []
    for answer in _res:
        index = in_list(answer, res)
        if answer.answer is not None and first.answer is not None and answer.answer == first.answer:
            continue
        if index is None:
            res.append(answer)
        else:
            if res[index].get_prob() < answer.get_prob():
                res[index] = answer
    return [first] + sorted(res, key=lambda x: x.get_prob(), reverse=True)


@lru_cache(maxsize=PAGE_CACHE_SIZE)
def compute(pinyin: str, width: int, error_correction, partical) -> List[Dict]:
    """
    Compute all probability of pinyin.
    LRU cache save time when you turn pages.
    :param pinyin: a string of pinyin.
    :param width: the maximum number of answers to be returned.
    :param error_correction: whether using error correction or not.
    :param partical: use shorter answer to increase accuracy.
    :return: JSON of pinyin sorted by probability.
    """
    common_cut, error_cut = cut(pinyin, error_correction)
    answers = []
    common_answers = []
    error_answers = []
    for c in common_cut:
        viterbi_result = viterbi(c, width)
        for r in viterbi_result:
            common_answers.append(r)
    for e in error_cut:
        viterbi_result = viterbi(e, width)
        for r in viterbi_result:
            error_answers.append(r)
    answers = merge(pinyin, common_answers, error_answers)
    if partical:
        if len(answers[0].answer)>2 and len(answers)!=1:
            two_words_cut=set([a.slice(2) for a in common_cut])
            one_word_cut=set([a.slice(1) for a in common_cut])
            _two_words_answers=[]
            _one_word_answers=[]
            for c in two_words_cut:
                viterbi_result = viterbi(c, width)
                for r in viterbi_result:
                    _two_words_answers.append(r)
            for c in one_word_cut:
                viterbi_result = viterbi(c, width)
                for r in viterbi_result:
                    _one_word_answers.append(r)
            two_words_answers=merge(pinyin, _two_words_answers, [])
            one_word_answers=merge(pinyin, _one_word_answers, [])
            if len(one_word_answers)==1:
                one_word_answers=[]
            if len(two_words_answers)==1:
                two_words_answers=[]
            answers=answers[:4]+two_words_answers[:3]+one_word_answers
    return [{
        'partition': r.partition,
        'probability': r.get_prob(),
        'process_to': r.process_to,
        'answer': r.answer
    } for r in answers]

def test():
    start=time.time()
    out=compute('nanjingdaxuerengongzhinengxueyuan', 10, True, False)
    print(time.time()-start)
    print(out)