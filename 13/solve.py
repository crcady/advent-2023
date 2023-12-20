from __future__ import annotations
import sys

class Pattern():
    def __init__(self, lines: list[str]):
        self.original = lines
        self.reflected: list[lines] = []
        self.h_mirror: int|None = None
        self.v_mirror: int|None = None

        self.v_mirror2: int|None = None
        self.h_mirror2: int|None = None

        self._find_h_reflect()
        self._find_v_reflect()

        for row in self.original:
            print(row)

        print('-----')

    def _find_h_reflect(self):
        for i in range(len(self.original)-1):
            n_above = i+1
            n_below = len(self.original) - n_above
            slice_size = min(n_above, n_below)
            above, below = [], []
            for j in range(slice_size):
                above.append(self.original[i-j])
                below.append(self.original[i+j+1])

            hamming = 0
            for (a, b) in zip(above, below):
                for j in range(len(a)):
                    if a[j] != b[j]:
                        hamming += 1

            if hamming == 0:
                self.h_mirror = i

            if hamming == 1:
                self.h_mirror2 = i


    def _find_v_reflect(self):
        cols:list[str] = ['' for i in range(len(self.original[0]))]

        for row in self.original:
            for i in range(len(row)):
                cols[i] += row[i]
        
        for i in range(len(cols)-1):
            n_left = i+1
            n_right = len(cols) - n_left
            slice_size = min(n_left, n_right)
            left, right = [], []
            for j in range(slice_size):
                left.append(cols[i-j])
                right.append(cols[i+j+1])
                        
            hamming = 0
            for (l, r) in zip(left, right):
                for j in range(len(l)):
                    if l[j] != r[j]:
                        hamming += 1
            
            if hamming == 0:
                self.v_mirror = i
            
            if hamming == 1:
                self.v_mirror2 = i


    def score1(self)->int:
        if self.v_mirror is not None:
            return self.v_mirror + 1
        if self.h_mirror is not None:
            return (self.h_mirror + 1) * 100
        
        for row in self.original:
            print(row)
        assert False, "No mirroring!"

    def score2(self)->int:
        if self.v_mirror2 is not None:
            return self.v_mirror2 + 1
        if self.h_mirror2 is not None:
            return (self.h_mirror2 + 1) * 100
        
        for row in self.original:
            print(row)
        assert False, "No mirroring!"


class Solver():
    def __init__(self, filename: str):
        self.patterns: list[Pattern] = []

        with open(filename, 'r') as f:
            current = []
            for line in f.readlines():
                if line.strip() != '':
                    current.append(line.strip())
                else:
                    self.patterns.append(Pattern(current))
                    current = []
            if len(current) > 0:
                self.patterns.append(Pattern(current))

    def solve1(self):
        return sum(p.score1() for p in self.patterns)

    def solve2(self):
        return sum(p.score2() for p in self.patterns)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver.solve2()}")