from __future__ import annotations
from dataclasses import dataclass
import re
import sys

type Part = dict[str, int]

@dataclass
class Expression:
    """Class for keeping track of an expression"""
    variable: str
    operator: str
    literal: int

    def check(self, values: Part)->bool:
        lhs = values[self.variable]
        if self.operator == '<':
            return lhs < self.literal
        else:
            return lhs > self.literal
        
    def negation(self)->Expression:
        if self.operator == '<':
            return Expression(self.variable, '>', self.literal - 1)
        else: # self.operation == '>'
            return Expression(self.variable, '<', self.literal + 1)

class Workflow:
    """CLass for holding a workflow"""

    def __init__(self, workflow_string: str):
        (name, remaining_string) = workflow_string.split('{')
        self.name = name
        values = remaining_string[:-1].split(',')
        self.rules: list[tuple[Expression, str]] = []
        for value in values:
            vals = value.split(':')
            if len(vals) < 2:
                self.default = value
            else:
                dest = vals[1]
                var = vals[0][0]
                op = vals[0][1]
                lit = int(vals[0][2:])
                self.rules.append((Expression(var, op, lit), dest))

    def getNextWorkflowName(self, part: Part)->str:
        """Return the name of the next workflow"""
        for rule in self.rules:
            if rule[0].check(part):
                return rule[1]
        return self.default

class ExpressionSet:
    """Class for evaluating conjunctions of expressions"""

    def __init__(self):
        self.expr_dict: dict[str, list[Expression]] = {x: [] for x in ['x','m','a','s']}

    def addExpr(self, expr: Expression):
        self.expr_dict[expr.variable].append(expr)

    @classmethod
    def copy(cls, instance: ExpressionSet)->ExpressionSet:
        es = cls()
        for l in instance.expr_dict.values():
            for expr in l:
                es.addExpr(expr)

        return es
    
    def count(self)->int:
        combos = 1
        #print('Counting an ExpressionSet')
        for cat, expr_list in self.expr_dict.items(): # This is safe because the constructor makes 4 entries

            lt = list(filter(lambda x: x.operator == '<', expr_list))
            gt = list(filter(lambda x: x.operator == '>', expr_list))

            if len(lt) > 0:
                lt.sort(key=lambda x: x.literal)
                lub = lt[0].literal
            else:
                lub = 4001
            
            if len(gt) > 0:
                gt.sort(key=lambda x: x.literal)
                glb = gt[-1].literal
            else:
                glb = 0
            
            combos *= (lub - glb - 1)

            #print(f'  {glb} < {cat} < {lub}: {lub - glb - 1}')

        #print(f'Total: {combos}')
        return combos

class Solver():
    def __init__(self, filename: str):
        self.parts: list[Part] = []
        self.workflows: list[Workflow] = []
        with open(filename, 'r') as f:
            finished_workflows = False
            for line in f:
                if line.strip() == '':
                    finished_workflows = True
                    continue

                if finished_workflows:
                    self.parts.append(self.parsePart(line.strip()))
                else:
                    self.workflows.append(Workflow(line.strip()))
            

    def parsePart(self, line: str)->Part:
        triples = line[1:-1].split(',')
        d = {}
        for t in triples:
            (name, value) = t.split('=')
            d[name] = int(value)
        return d
    
    def scorePart(self, part: Part)->int:
        return sum(part.values())

    def solve1(self):
        work_queue: list[tuple[Part, str]] = [(p, 'in') for p in self.parts]
        accepted: list[Part] = []
        rejected: list[Part] = []
        workflow_dict = {wf.name: wf for wf in self.workflows}

        while work_queue:
            (p, dest) = work_queue.pop()
            current_wf = workflow_dict[dest]
            next_wf_name = current_wf.getNextWorkflowName(p)
            if next_wf_name == 'A':
                accepted.append(p)
            elif next_wf_name == 'R':
                rejected.append(p)
            else:
                work_queue.append((p, next_wf_name))
        
        return sum(self.scorePart(p) for p in accepted)

    def solve2(self):
        # We want to end up with a list of ExpressionSet s that result in a part being accepted.
        work_queue: list[tuple[ExpressionSet, str]] = [(ExpressionSet(), 'in')]
        workflow_dict = {wf.name: wf for wf in self.workflows}
        accepted_list: list[ExpressionSet] = []

        while work_queue:
            (es, dest) = work_queue.pop()

            if dest == 'A':
                accepted_list.append(es)
                continue
            if dest == 'R':
                continue

            current_wf = workflow_dict[dest]
            for (expr, next_dest) in current_wf.rules:
                # expr is satisfied
                satisfied_es = ExpressionSet.copy(es)
                satisfied_es.addExpr(expr)
                work_queue.append((satisfied_es, next_dest))

                # expr is not satisfied
                es.addExpr(expr.negation())

            # No rules were satisfied, so we need to work on the default
            work_queue.append((es, current_wf.default))


        return sum(es.count() for es in accepted_list)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver.solve2()}")