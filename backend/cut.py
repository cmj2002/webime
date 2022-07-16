"""
Author: Cao Ming jun
Date: 2022-07-10
Description: Cut sequence of pinyin into set of valid array of pinyin.
"""
from typing import Set, Dict, Tuple
from backend.classes import Answer
import itertools
from backend.utils import ERROR_CORRECTION_DEGRADE,ROOT

# Load valid pinyin string
with open(f"{ROOT}/data/valid.txt") as f:
    valid_pinyin = set(f.read().splitlines())
assert all(len(x) <= 6 for x in valid_pinyin)
## Generate prefix for valid pinyin
pinyin_prefix = dict()
for _pinyin in valid_pinyin:
    for _i in range(1, len(_pinyin) + 1):
        pinyin_prefix[_pinyin[:_i]] = pinyin_prefix.get(_pinyin[:_i], []) + [_pinyin]


def cut_main(pinyin: str, complete: bool = False) -> Set[Answer]:
    """
    Cut sequence of pinyin into set of valid array of pinyin. Sequence should not contain break.
    :param pinyin: sequence of pinyin
    :param complete: whether using complete match or not
    :return: set of Answer instances.
    """
    ans = set() if pinyin not in pinyin_prefix else {Answer([pinyin], 1.0)}
    for i in range(1, len(pinyin)):
        if pinyin[:i] in valid_pinyin:
            appendices = cut_main(pinyin[i:], complete)
            for appendix in appendices:
                ans.add(Answer([pinyin[:i]], 1.0) + appendix)
        elif (not complete) and (pinyin[:i] in pinyin_prefix.keys()):
            appendices = cut_main(pinyin[i:], complete)
            for appendix in appendices:
                # degrade is did when generating emission matrix
                ans.add(Answer([pinyin[:i]], 1.0) + appendix)
    return ans


def cut_with_error_correction(pinyin: str) -> Dict[str, Set[Answer]]:
    """
    Exchange nearby character one by one and try to cut.
    :param pinyin:
    :return: set of Answer instances.
    """
    ans = {}
    for i in range(1, len(pinyin) - 1):
        key = pinyin[:i] + pinyin[i + 1] + pinyin[i] + pinyin[i + 2:]
        value = cut_main(key)
        for answer in value:
            answer.degrade(ERROR_CORRECTION_DEGRADE)
        if value:
            ans[key] = value
    ans['all'] = set([p for t in ans.values() for p in t])
    return ans


def cut(pinyin: str, error_correction: bool = True) -> Tuple[Set[Answer]]:
    """
    Cut sequence of pinyin into set of valid array of pinyin.
    :param pinyin: sequence of pinyin
    :param error_correction: whether using error correction or not
    :return: set of Answer instances.
    """
    # handle breaks
    if r"'" in pinyin:
        ans: Set[Answer] = set()
        pieces = [x for x in pinyin.split(r"'") if len(x) > 0]
        cuts: Dict[str, Set[Answer]] = {}
        for piece in pieces:
            cuts[piece] = cut(piece, error_correction)
        cartesian = itertools.product(*cuts.values())
        for case in cartesian:
            ans.add(Answer.concat(case))
        return ans
    else:
        if error_correction:
            return cut_main(pinyin) , cut_with_error_correction(pinyin)['all']
        else:
            return cut_main(pinyin) , set()


if __name__ == "__main__":
    test_input = input("Input pinyin: ")
    test_ans = cut(test_input)
    print(f"Get {len(test_ans)} answers: ")
    for test_answer in sorted(list(test_ans), key=lambda x: x.prior, reverse=True):
        print(str(test_answer.prior), ":", test_answer)
    print("\n")
    # test_ans = cut_main(test_input, False)
    # print(f"Get {len(test_ans)} answers: ")
    # for test_answer in sorted(list(test_ans), key=lambda x: x.prior, reverse=True):
    #     print(str(test_answer.prior), ":", test_answer)
    # print("\n")
    # test_ans = cut_with_error_correction(test_input)
    # print(f"Get {len(test_ans['all'])} answers with error correction: ")
    # for test_answer in sorted(list(test_ans['all']), key=lambda x: x.prior, reverse=True):
    #     print(str(test_answer.prior), ":", test_answer)
