import sys
from z3 import *
from timeit import default_timer as timer
import matplotlib.pyplot as plt

def parse(fname) -> dict[int, int]:
    res = {0: 1}
    with open(fname, "r") as file:
        for line in file:
            steps, plots, _ = line.split(",")
            res[int(steps)] = int(plots)

    return res

def plot(results: dict[int, int]):
    x = [i for i in range(len(results)+1) if i % 50 == 0]
    y = [results[i] for i in x]

    fix, ax = plt.subplots()
    ax.plot(x, y)
    plt.show()

def poly(results: dict[int, int]) -> bool:
    # Assume that after some amount of time, the number of steps is defined by the equation:
    # y = ax^4 + bx^3 + cx^2 + dx + e
    # Also assume that those are integers, because there's no reason to think they wouldn't be

    a = Int("a")
    b = Int("b")
    c = Int("c")
    d = Int("d")
    e = Int("e")

    s = Solver()

    # Having more than 5 points over-constraints the problem, but if it doens't generalize a bit farther, it isn't useful
    for i in range(len(results)-10, len(results)):
        x = Int("x_"+str(i))
        y = Int("y_"+str(i))
        s.add(x*x*x*x*a + x*x*x*b + x*x*c + x*d + e == y, x == i, y == results[i])

    res = s.check()

    if res == unsat:
        return False
    else:
        print(res.model())
        return True
    

def difference(results: dict[int, int]) -> bool:
    # Assume that after some amount of time, the next value y_n can be computed by:
    # y_n = x_1*y_{n-1} + x_2* y_{n-2} ... x_m*y_{n-m}
    # I don't think we need to know m ahead of time, if we choose a sufficiently large m for the solver
    # Any unneeded coefficients should come back as 0 in the model
    # In order to have enough constraints to get a meaningful answer, we can use a sliding window

    m = 25

    x_m = [Int("x_"+str(i+1)) for i in range(m)] # the zero-th element is x_1, the x_m[m-1] == x_m from the equation above

    s = Solver()

    for i in range(m):
        n = len(results)- i - 1
        y = results[n]
        current = 0
        for j in range(m):
            current = x_m[j]*results[n-j-1] + current

        s.add(current == y)

    res = s.check()
    if res == unsat:
        return False
    else:
        model = s.model()
        coeffs = [model[x].as_long() for x in x_m]
        window = [results[i] for i in range(len(results)-m-1, len(results))]
        print(f"Window: {window}")
        print(f"Coeffs: {coeffs}")
        n = len(results) - 1 # n holds the step index of the last element of the window
        while n < 3500:
            # Shift the values over by 1
            for i in range(len(window) - 1):
                window[i] = window[i+1]
            
            # Compute the new last element
            temp = 0
            for i in range(len(coeffs)):
                temp += coeffs[i]*window[len(window)-i-1]
            window[-1] = temp
            n += 1
            print(f"steps: {n}, plots: {window[-1]}")
        print(window[-1])
        return True
            
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename> [plot]")
        exit(1)

    fname = sys.argv[1]
    start = timer()
    results = parse(fname)
    end = timer()

    print(f"Parsed {len(results)} points in {end - start} seconds")

    if len(sys.argv) > 2:
        if sys.argv[2] == "plot":
            plot(results)
            exit(0)

    print("Trying for a 4th-order polynomial", end="...")
    res = poly(results)
    if res:
        exit(0) #Model will have been printed
    else:
        print("failed.")

    print("Trying difference equations", end="...")
    res = difference(results)
    if res:
        exit(0) #Model will have been printed
    else:
        print("failed.")

                