"""
Author: Cao Ming jun
Date: 2022-07-10
Description: Global utils.
"""

import os
from typing import Generator, Tuple, List, Dict, Set, Optional
import json
from tqdm import trange, tqdm

# working directory
ROOT=os.path.dirname(os.path.abspath(__file__))

# constants
START_VECTOR_FILE = ROOT+'/data/start_vector.json'
TRANSITION_MATRIX_FILE = ROOT+'/data/transition_matrix.json'
EMISSION_MATRIX_FILE = ROOT+'/data/emission_matrix.json'
REVERSE_EMISSION_FILE = ROOT+'/data/reverse_emission.json'
UNITED_REVERSE_FILE = ROOT+'/data/united_reverse.json'
INCOMPLETE_DEGRADE = 0.40
COMMON_INCOMPLETE_DEGRADE = 0.75
ERROR_CORRECTION_DEGRADE = 0.125

# environment variables
if 'PAGE_CACHE_SIZE' in os.environ:
    PAGE_CACHE_SIZE = int(os.environ['PAGE_CACHE_SIZE'])
else:
    PAGE_CACHE_SIZE = 32


def is_chinese(char: str) -> bool:
    assert len(char) == 1
    return u'\u4e00' <= char <= u'\u9fff'


def read_data() -> Generator[Tuple[str, int], None, None]:
    with open(f'{ROOT}/data/global_wordfreq.release.txt', 'r', encoding='utf-8') as f:
        for line in f:
            try:
                a, b = line.split()
                if all([is_chinese(x) for x in a]):
                    yield a, int(b)
            except Exception as e:
                continue

def save_json(data: dict, file_path: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)

def load_json(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize(pinyin: str):
    """
    Turn all 've' to 'ue'.
    """
    return pinyin.replace('ve', 'ue', -1)
