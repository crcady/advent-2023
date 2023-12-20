from __future__ import annotations
import sys

class Solver:
    def __init__(self, filename):
        self.nums:list[list[int]] = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                self.nums.append([int(x) for x in line.split()])

    def solve1(self):
        results = [self.solve_line(x) for x in self.nums]
        return sum(results)
    
    def solve2(self):
        results = [self.solve_line2(x) for x in self.nums]
        return sum(results)

    def solve_line(self, line: list[int])->int:
        first = line[0]
        if line.count(first) == len(line):
            return first
        
        next_line = [line[x+1] - line[x] for x in range(len(line) - 1)]
        return line[-1] + self.solve_line(next_line)
    
    def solve_line2(self, line: list[int])->int:
        first = line[0]
        if line.count(first) == len(line):
            return first
        
        next_line = [line[x+1] - line[x] for x in range(len(line) - 1)]
        result = self.solve_line2(next_line)
        return line[0] - result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"Sum: {solver.solve1()}")
    print(f"Sum: {solver.solve2()}")