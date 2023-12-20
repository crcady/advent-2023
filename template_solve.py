from __future__ import annotations
import sys

class Solver():
    def __init__(self, filename: str):
        with open(filename, 'r') as f:
            pass

    def solve1(self):
        pass

    def solve2(self):
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver.solve2()}")