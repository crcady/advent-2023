from __future__ import annotations
import sys

class Solver():
    def __init__(self, filename: str):
        with open(filename, 'r') as f:
            strings = f.read().split(',')

        self.strings = strings

    def compute(self, string:str)->int:
        n = 0
        for s in string:
            n += ord(s)
            n *= 17
            n = n % 256
        
        return n

    def solve1(self):
        hashes = [self.compute(s) for s in self.strings]
        print(f"Hashes range from {min(hashes)} to {max(hashes)}")
        return sum(hashes)

    def solve2(self):
        boxes: list[list[tuple[str, int]]] = [[] for i in range(256)]

        for s in self.strings:
            if s[-2] == '=':
                # Then we have something of the form {label}={focal_length}
                label = s[:-2]
                focal_length = int(s[-1])
                boxnum = self.compute(label)
                found = False
                for i in range(len(boxes[boxnum])):
                    if boxes[boxnum][i][0] == label:
                        # We found one!
                        found = True
                        boxes[boxnum][i] = (label, focal_length)
                if not found:
                    boxes[boxnum].append((label, focal_length))
                    
            else:
                # Then we have something of the form {label}-
                label = s[:-1]
                boxnum = self.compute(label)
                found = None
                for i in range(len(boxes[boxnum])):
                    if boxes[boxnum][i][0] == label:
                        # We found one!
                        found = i
                if found is not None:
                    boxes[boxnum].pop(found)

            # print(f'After "{s}":')
            # for i in range(256):
            #     if len(boxes[i]) == 0:
            #         continue
            #     print(f"Box {i}: {boxes[i]}")
            # print()

        power = 0
        for i in range(256):
            for j in range(len(boxes[i])):
                power += (i + 1) * (j + 1) * boxes[i][j][1]

        return power


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver.solve2()}")