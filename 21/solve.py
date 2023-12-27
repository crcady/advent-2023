from __future__ import annotations
import sys

type Coord = tuple[int, int]

class Solver():
    def __init__(self, filename: str):
        self.reachable:set[Coord] = set()
        row_number = 0
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                col_number = 0
                for char in line:
                    if char == 'S':
                        self.start = (row_number, col_number)
                        self.reachable.add((row_number, col_number))

                    elif char == '.':
                        self.reachable.add((row_number, col_number))

                    col_number += 1
                row_number += 1

        self.height = row_number
        self.width = col_number

    def solve1(self, steps: int):
        reachable_sets: list[set[Coord]] = [set([self.start])]
        for i in range(steps):
            new_set = set()
            for (x, y) in reachable_sets[-1]:
                for coord in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
                    if coord in self.reachable:
                        new_set.add(coord)
            reachable_sets.append(new_set)

        return len(reachable_sets[-1])

    def solve2(self, steps:int):
        last_set = set([self.start])
        for i in range(steps):
            new_set = set()
            for (x, y) in last_set:
                for (i, j) in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
                    if (i % self.height, j % self.width) in self.reachable:
                        new_set.add((i, j))
            last_set = new_set

        return len(last_set)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1(6)}")
    print(f"Second Solution: {solver.solve2(500)}")