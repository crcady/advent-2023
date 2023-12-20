from __future__ import annotations
import sys

class Solver():
    def __init__(self, filename: str, expansion:int = 2):
        self.image: list[list[str]] = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                self.image.append(line.strip())

        self.expand(expansion)
    
    def expand(self, expansion):
        rows:set[int] = set()
        cols:set[int] = set()
        stars: set[tuple[int, int]] = set()
        expanded_stars: set[tuple[int, int]] = set()

        for i in range(len(self.image)):
            row = self.image[i]
            for j in range(len(row)):
                if row[j] == '#':
                    rows.add(i)
                    cols.add(j)
                    stars.add((i, j))

        current_x = -1
        current_y = -1

        for x in range(len(self.image)):
            if x in rows:
                current_x +=1
            else:
                current_x += expansion

            current_y = -1
            for y in range(len(self.image[x])):
                if y in cols:
                    current_y += 1
                else:
                    current_y += expansion

                if (x, y) in stars:
                    expanded_stars.add((current_x, current_y))

        self.stars = stars
        self.expanded_stars = expanded_stars

    def manhattan_distance(self, a: tuple[int, int], b: tuple[int, int])->int:
        dx = abs(b[0] - a[0])
        dy = abs(b[1] - a[1])
        return dx + dy 

    def solve1(self):
        star_list = list(self.expanded_stars)
        distances: list[int] = []
        for i in range(len(star_list)):
            for j in range(i+1, len(star_list)):
                a = star_list[i]
                b = star_list[j]
                distances.append(self.manhattan_distance(a, b))

        return sum(distances)

    def solve2(self):
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)
    solver2 = Solver(filename, expansion=1000000)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver2.solve1()}")