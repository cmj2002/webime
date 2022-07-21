from copy import deepcopy
from math import log


class Answer:
    def __init__(self, partition: list, prior: float):
        self.partition = partition
        self.prior = prior
        self.answer = None
        self.probability = None
        # index of last character that successfully processed by viterbi
        self.process_to: int = 0

    def set_answer(self, answer: str, probability: float, process_to: int):
        new_answer = deepcopy(self)
        new_answer.answer = answer
        new_answer.probability = probability
        new_answer.process_to = process_to
        return new_answer

    def append(self, sub_partition: str) -> None:
        self.partition.append(sub_partition)

    def degrade(self, degradation: float) -> None:
        self.prior *= degradation

    def slice(self, len):
        res=deepcopy(self)
        res.partition=res.partition[:len]
        return res

    def get_index(self) -> int:
        return len(''.join(self.partition))

    def get_prob(self) -> float:
        assert self.probability is not None
        return (log(self.prior) + self.probability)/len(self.answer)

    def get_origin(self) -> str:
        return ''.join(self.partition)

    # plus
    def __add__(self, other):
        return Answer(self.partition + other.partition, self.prior * other.prior)

    @staticmethod
    def concat(answers):
        temp = deepcopy(answers[0])
        for i in range(1, len(answers)):
            temp += answers[i]
        return temp

    def __str__(self):
        if self.answer:
            return self.answer
        else:
            return str(self.partition)

    def __repr__(self):
        if self.answer:
            return self.answer
        else:
            return str(self.partition)
