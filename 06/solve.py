import sys

class Solver:
    def __init__(self, filename: str):
        with open(filename, 'r') as f:
            timeline = f.readline()
            distanceline = f.readline()

        times = timeline.split()
        assert(times[0] == "Time:")

        distances = distanceline.split()
        assert(distances[0] == "Distance:")

        times = [int(t) for t in times[1:]]
        distances = [int(d) for d in distances[1:]]

        self.pairs = list(zip(times, distances))

        times = timeline.split()[1:]
        distances = distanceline.split()[1:]

        bigtime = ''.join(times)
        bigdistance = ''.join(distances)

        self.bigtime = int(bigtime)
        self.bigdistance = int(bigdistance)

    def race(self, holdtime, racetime)->int:
        """Returns the distance traveled"""
        speed = holdtime
        movingtime = racetime - holdtime
        distance = speed*movingtime
        return distance
    
    def countwins(self, racetime: int, record: int):
        count = 0
        for i in range(racetime): # skips the last time, but that will always be zero
            if self.race(i, racetime) > record:
                count += 1

        return count

    def solve1(self)->int:
        margins: list[int] = []
        for t, d in self.pairs:
            count = self.countwins(t, d)
            margins.append(count)

        product = 1
        for m in margins:
            product *= m
        
        print(margins)
        return product
    
    def solve2(self)->int:
        return self.countwins(self.bigtime, self.bigdistance)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)
    print(f"The margin product was {solver.solve1()}")
    print(f"The number of wins was {solver.solve2()}")
