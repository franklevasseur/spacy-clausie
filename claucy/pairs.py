from typing import List, Tuple


def getPairs(n):
    pairs: List[Tuple[int, int]] = []
    for i in range(n):
        for j in range(i, n):
            if i == j:
                continue

            pairs.append((i, j))
    return pairs
