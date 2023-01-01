"""NFA and DFA Library.

References:
    - https://en.wikipedia.org/wiki/Powerset_construction#CITEREFHopcroftUllman1979
    - https://www.youtube.com/watch?v=jMxuL4Xzi_A&ab_channel=EasyTheory
"""

from __future__ import annotations
from collections import deque

from dataclasses import dataclass
from itertools import filterfalse
from pprint import pprint

State = frozenset[str] | str

LAMBDA = ""  # Represents lambda transition in an NFA.


@dataclass
class DFA:
    states: set[State]
    alphabet: set[str]
    transfunc: dict[State, dict[str, State]]
    initial: State
    accepting: set[State]

    def check(self, string: str) -> list[State]:
        curr = self.initial
        path = [curr]
        for char in string:
            path.append(curr := self.transfunc[curr][char])
        return [] if path[-1] not in self.accepting else path

    def to_regex(self) -> str:
        ...  # To be implemented.


class NFA(DFA):
    def powerset_construct(self) -> DFA:
        """Powerset construction of a DFA from an NFA.

        The following code is 100% my own and took a while to figure out how to implement.
        This is still very much untested, so use at your own risk!
        """
        # The code below is going to be refactored and have more comments
        # that give a better explanation as to the process of powerset
        # construction from an NFA to a DFA.

        # Get all lambda transitions from the NFA.
        lambda_trans = {}
        for state, edges in self.transfunc.items():
            for letter in filterfalse(None, edges):
                lambda_trans[state] = edges[letter]
        visited = set()
        init = self.initial
        new_state = frozenset({init})
        new_trans = {}
        queue = deque()
        first = True
        while first or queue:
            # This part is necessary since the initial state is processed
            # differently from later states in the powerset construction
            # process.
            if first:
                state = init
                while state in lambda_trans:
                    state = lambda_trans[state]
                    new_state |= {state}
                queue.appendleft(new_state)
                init = new_state
                first = False
            else:
                new_state = queue.pop()
                if new_state in visited:
                    continue
            sym_map = {}
            for sym in self.alphabet:
                sym_state = frozenset()
                for state in new_state:
                    trans = self.transfunc[state].get(sym)
                    if trans is not None:
                        if isinstance(trans, str):
                            # Check if any other "sub-states" are reachable using lambda transitions.
                            if trans in lambda_trans:
                                s = trans
                                trans = frozenset({trans})
                                while s in lambda_trans:
                                    s = lambda_trans[s]
                                    trans |= {s}
                        else:
                            # Check if any other "sub-states" are reachable using lambda transitions
                            # for each state in the trans set.
                            for s in trans:
                                if s in lambda_trans:
                                    r = s
                                    while r in lambda_trans:
                                        r = lambda_trans[r]
                                        trans |= {r}
                        sym_state |= {trans} if isinstance(trans, str) else trans
                        for s in sym_state:
                            r = s
                            while r in lambda_trans:
                                sym_state |= {r}
                                r = lambda_trans[r]
                sym_map[sym] = sym_state
            new_trans[new_state] = sym_map
            for sym in self.alphabet:
                queue.appendleft(new_trans[new_state][sym])
            visited.add(new_state)
        df = DFA(
            self.states.copy(),
            self.alphabet.copy(),
            new_trans,
            init,  # type: ignore
            accepting=set(),
        )
        for state in new_trans:
            if state & self.accepting:
                df.accepting.add(state)
        return df

    to_dfa = powerset_construct

    @classmethod
    def union(cls, *dfas: DFA) -> DFA:
        ...  # To be implemented!

    def check(self, string: str) -> list[State]:
        return self.powerset_construct().check(string)


if __name__ == "__main__":
    a = NFA(
        states={"q0", "q1", "q2", "q3"},
        alphabet={"0", "1"},
        transfunc={
            "q0": {"": "q2", "0": "q1"},
            "q1": {"1": frozenset({"q1", "q3"})},
            "q2": {"": "q1", "0": "q3"},
            "q3": {"0": "q2"},
        },
        initial="q0",
        accepting={"q2", "q3"},
    )

    b = NFA(
        states={"q0", "q1", "q2", "q3"},
        alphabet={"a", "b"},
        transfunc={
            "q0": {"": "q1"},
            "q1": {"a": frozenset({"q1", "q2"}), "b": "q2"},
            "q2": {"a": frozenset({"q0", "q2"}), "b": "q3"},
            "q3": {"b": "q1"},
        },
        initial="q0",
        accepting={"q0"},
    )
    x = a.to_dfa()
    pprint(x)
    print()
    y = b.to_dfa()
    pprint(y)
