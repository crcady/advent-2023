from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import sys

type Point2D = tuple[float, float]
type Point3D = tuple[float, float, float]


@dataclass
class Hailstone:
    position: Point3D
    velocity: Point3D

    @classmethod
    def from_line(cls, line: str) -> Hailstone:
        p, v = line.split("@")
        (px, py, pz) = p.split(",")
        (vx, vy, vz) = v.split(",")
        return Hailstone(
            (float(px), float(py), float(pz)), (float(vx), float(vy), float(vz))
        )
    
    def getXYintersection(self, other: Hailstone)->Point2D|None:
        A = np.array([[self.velocity[0], -self.velocity[1]],
                      [other.velocity[0], -other.velocity[1]]])
        
        B = np.array([[self.velocity[0] * self.position[1] - self.velocity[1] * self.position[0]],
                      [other.velocity[0] * other.position[1] - other.velocity[1] * other.position[0]]])
        
        if np.linalg.det(A) == float(0):
            return None
        
        invA = np.linalg.inv(A)

        X = np.matmul(invA, B)

        x = X[1][0]
        y = X[0][0]

        return (x, y)
    
    def getTime2D(self, point: Point2D)->float:
        x = point[0]
        return (x - self.position[0]) / self.velocity[0]


class Solver:
    def __init__(self, filename: str):
        self.hailstones: list[Hailstone] = []
        with open(filename, "r") as f:
            for line in f:
                self.hailstones.append(Hailstone.from_line(line))

    def solve1(self, XYmin, XYmax):
        found = 0
        for i in range(len(self.hailstones)):
            for j in range(i+1, len(self.hailstones)):
                first = self.hailstones[i]
                second = self.hailstones[j]

                point = first.getXYintersection(second)
                if point is not None and first.getTime2D(point) > 0 and second.getTime2D(point) > 0 and point[0] >= XYmin and point[0] <= XYmax and point[1] >= XYmin and point[1] <= XYmax:
                    found += 1

        return found


    def solve2(self):
        pass


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        XYmin, XYmax = 200000000000000, 400000000000000
    else:
        filename = "tiny_input"
        XYmin, XYmax = 7, 27

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1(XYmin, XYmax)}")
    print(f"Second Solution: {solver.solve2()}")
