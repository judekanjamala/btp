from enum import Enum
from random import random
from math import inf
from functools import reduce

# TODO: Clarify state transition with regards to prerequisite states.
# TODO: Come up with a better return value for solve.

class KC_STATE(Enum):
    NOT_LEARNED = 0
    LEARNED = 1

class Student(object):

    def __init__(self,
                 kc_states,
                 pt,
                 ps,
                 pg,
                 get_prerequisites,
                 get_kc,
                 get_solution):
        self.kc_states = {kc: KC_STATE.NOT_LEARNED if s == 0 else KC_STATE.LEARNED for (kc, s) in kc_states.items()}
        self.pt = pt
        self.ps = ps
        self.pg = pg
        self._get_prerequisites = get_prerequisites
        self._get_kc = get_kc
        self._get_solution = get_solution

        return

    def _update_state(self, kc, pre_reqs):
        if any([self.kc_states[x] == KC_STATE.NOT_LEARNED for x in pre_reqs]):
            p_t = self.pt[kc]["low"]
        else: 
            p_t = self.pt[kc]["high"]

        if random() < p_t:
            self.kc_states[kc] = KC_STATE.LEARNED
        
        return

    def solve(self, problem):
        kc = self._get_kc(problem)
        pre_reqs = self._get_prerequisites(kc)
        self._update_state(kc, pre_reqs)

        p_kcs = [(1 - self.ps[x]) if self.kc_states[x] == KC_STATE.LEARNED else self.pg[x] for x in pre_reqs]
        p_kcs.append((1 - self.ps[kc]) if self.kc_states[kc] == KC_STATE.LEARNED else self.pg[kc])
        p_solving = reduce(lambda x, y: x * y, p_kcs, 1)

        solution = self._get_solution(problem) if random() < p_solving else -inf
        
        return solution
   
    def status(self):
        status = [f"\nState of KC {x[0]} is {x[1]}." for x in self.kc_states.items()]
        return ("").join(status)
    