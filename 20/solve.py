from __future__ import annotations
from collections import deque
from dataclasses import dataclass
import sys


@dataclass
class Pulse:
    source: str
    destination: str
    high: bool


@dataclass
class Module:
    """Basic untyped module class"""

    name: str
    outputs: list[str]
    pulse_queue: deque[Pulse]

    def emit_low(self) -> None:
        self.pulse_queue.extendleft(Pulse(self.name, o, False) for o in self.outputs)

    def emit_high(self) -> None:
        self.pulse_queue.extendleft(Pulse(self.name, o, True) for o in self.outputs)

    def receive(self, pulse: Pulse) -> None:
        pass


class Broadcast(Module):
    def receive(self, pulse: Pulse) -> None:
        if pulse.high:
            self.emit_high()
        else:
            self.emit_low()


@dataclass
class FlipFlop(Module):
    current_state: bool = False

    def receive(self, pulse: Pulse) -> None:
        if pulse.high:
            pass
        else:
            if self.current_state:
                self.current_state = False
                self.emit_low()
            else:
                self.current_state = True
                self.emit_high()


@dataclass
class Conjunction(Module):
    def __post_init__(self):
        self.inputs: dict[str, bool] = {}

    def add_input(self, input_name: str):
        self.inputs[input_name] = False

    def receive(self, pulse: Pulse) -> None:
        self.inputs[pulse.source] = pulse.high
        for v in self.inputs.values():
            if not v:
                self.emit_high()
                return

        self.emit_low()


class Circuit:
    def __init__(self):
        self.modules: dict[str, Module] = {}
        self.pulse_queue: deque[Pulse] = deque()
        self.dirty: bool = False
        self.low_count: int = 0
        self.high_count: int = 0
        self.pulse_log: list[Pulse] = []

    def add_broadcast(self, outputs: list[str]):
        self.modules["broadcast"] = Broadcast("broadcast", outputs, self.pulse_queue)

    def add_flipflop(self, name: str, outputs: list[str]):
        self.modules[name] = FlipFlop(name, outputs, self.pulse_queue)

    def add_conjunction(self, name: str, outputs: list[str]):
        self.modules[name] = Conjunction(name, outputs, self.pulse_queue)
        self.dirty = True

    def finalize(self):
        if self.dirty:
            for m in self.modules.values():
                if m.__class__ == Conjunction:
                    for mod in filter(
                        lambda x: m.name in x.outputs, self.modules.values()
                    ):
                        m.add_input(mod.name)
            self.dirty = False

    def dispatch(self, pulse: Pulse):
        # print(f'{pulse.source} -{pulse.high}-> {pulse.destination}')
        self.pulse_log.append(pulse)
        if pulse.high:
            self.high_count += 1
        else:
            self.low_count += 1

        if pulse.destination in self.modules:
            self.modules[pulse.destination].receive(pulse)

    def press(self):
        self.finalize()
        self.pulse_log = []

        self.pulse_queue.append(Pulse("button", "broadcast", False))

        while self.pulse_queue:
            self.dispatch(self.pulse_queue.pop())

    def score(self) -> int:
        return self.low_count * self.high_count


class Solver:
    def __init__(self, filename: str):
        self.circuit = Circuit()

        with open(filename, "r") as f:
            for line in f:
                (name, outputs) = line.split("-")
                name = name.strip()
                outputs = outputs[1:].strip().split(",")
                outputs = [x.strip() for x in outputs]

                if name == "broadcaster":
                    self.circuit.add_broadcast(outputs)

                elif name[0] == "%":
                    self.circuit.add_flipflop(name[1:], outputs)

                elif name[0] == "&":
                    self.circuit.add_conjunction(name[1:], outputs)

    def solve1(self):
        for i in range(1000):
            self.circuit.press()

        return self.circuit.score()

    def solve2(self, target_output: str, target_high: bool):
        count = 0
        to_watch = ["mp", "qt", "qb", "ng"]
        while to_watch:
            for p in self.circuit.pulse_log:
                if p.high and p.source in to_watch:
                    print(f"{p.source} sent a high pulse with count={count}")
                    to_watch.remove(p.source)
            self.circuit.press()
            count += 1
            if count > 10000:
                break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    # Creating a new solver is easier than resetting the state
    solver2 = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver2.solve2(target_output='rx', target_high=False)}")
