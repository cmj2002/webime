"""
Author: Cao Ming jun
Date: 2022-07-10
Description: Cut sequence of pinyin into set of valid array of pinyin.
"""
from copy import deepcopy
from typing import Set, Dict, Tuple
from backend.classes import Answer
import itertools
from backend.utils import ERROR_CORRECTION_DEGRADE, ROOT

# Load valid pinyin string
with open(f"{ROOT}/data/valid.txt") as f:
    valid_pinyin = set(f.read().splitlines())
assert all(len(x) <= 6 for x in valid_pinyin)
# Generate prefix for valid pinyin
pinyin_prefix = set()
pinyin_head = set()
for _pinyin in valid_pinyin:
    pinyin_head.add(_pinyin[0])
    for _i in range(1, len(_pinyin)):
        pinyin_prefix.add(_pinyin[:_i])
headSet = valid_pinyin | pinyin_head
anySet = valid_pinyin | pinyin_prefix | pinyin_head


def cut_main(pinyin: str, acceptHead: bool = False, acceptAny: bool = False) -> Set[Answer]:
    """
    Cut sequence of pinyin into set of valid array of pinyin. Sequence should not contain break.
    :param pinyin: sequence of pinyin
    :param complete: whether using complete match or not
    :return: set of Answer instances.
    """
    accepted = valid_pinyin
    if acceptHead:
        accepted = headSet
    if acceptAny:
        accepted = anySet
    ans = set() if len(pinyin) > 1 else {Answer([pinyin], 1.0)}
    for i in range(1, len(pinyin)+1):
        if pinyin[:i] in accepted:
            if i==len(pinyin):
                ans.add(Answer([pinyin[:i]], 1.0))
                continue
            appendices = cut_main(pinyin[i:], acceptHead, acceptAny)
            for appendix in appendices:
                ans.add(Answer([pinyin[:i]], 1.0) + appendix)
        if i==len(pinyin) and pinyin[:i] in anySet:
            ans.add(Answer([pinyin[:i]], 1.0))
    return ans


def cut_with_error_correction(pinyin: str, acceptHead: bool = False, acceptAny: bool = False) -> Dict[str, Set[Answer]]:
    """
    Exchange nearby character one by one and try to cut.
    :param pinyin:
    :return: set of Answer instances.
    """
    ans = {}
    for i in range(1, len(pinyin) - 1):
        key = pinyin[:i] + pinyin[i + 1] + pinyin[i] + pinyin[i + 2:]
        value = cut_main(key, acceptHead, acceptAny)
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
            tmp = cut(piece, error_correction)
            cuts[piece] = tmp[0] | tmp[1]
        cartesian = itertools.product(*cuts.values())
        for case in cartesian:
            if len(case) >= 1:
                ans.add(Answer.concat(case))
        return ans, set()
    else:
        ans: Set[Answer] = cut_main(pinyin, False, False)
        err_ans: Set[Answer] = cut_with_error_correction(pinyin, False, False)["all"] if error_correction else set()
        # TODO: just set len here at 23:56
        if len(ans) == 0:
            ans = cut_main(pinyin, True, False)
            err_ans = cut_with_error_correction(pinyin, True, False)["all"] if error_correction else set()
        if len(ans) == 0:
            ans = cut_main(pinyin, True, True)
        return ans, err_ans


def testCut():
    test_input = input("Input pinyin: ")

    print("Testing cut...")
    _test_ans = cut(test_input)
    test_ans=_test_ans[0] | _test_ans[1]
    print(f"Get {len(test_ans)} answers: ")
    for test_answer in sorted(list(test_ans), key=lambda x: x.prior, reverse=True):
        print(str(test_answer.prior), ":", test_answer)
    print("\n")

    # test_ans = cut_main(test_input, False, False)
    # print(f"Get {len(test_ans)} answers: ")
    # for test_answer in sorted(list(test_ans), key=lambda x: x.prior, reverse=True):
    #     print(str(test_answer.prior), ":", test_answer)
    # print("\n")

    # test_ans = cut_with_error_correction(test_input)
    # print(f"Get {len(test_ans['all'])} answers with error correction: ")
    # for test_answer in sorted(list(test_ans['all']), key=lambda x: x.prior, reverse=True):
    #     print(str(test_answer.prior), ":", test_answer)
