"""NFA and DFA Library.

References:
    - https://en.wikipedia.org/wiki/Powerset_construction#CITEREFHopcroftUllman1979
    - https://www.youtube.com/watch?v=jMxuL4Xzi_A&ab_channel=EasyTheory
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from functools import reduce
from itertools import filterfalse
from operator import ior
from pprint import pprint

State = frozenset[str] | set[str] | str

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
    def lambda_trans(self) -> dict[State, State]:
        """Returns all lambda transitions in the form of state pairs."""
        lambda_trans = {}
        for state, edges in self.transfunc.items():
            for letter in filterfalse(None, edges):
                lambda_trans[state] = edges[letter]
        return lambda_trans

    def powerset_construct(self) -> DFA:
        """Powerset construction of a DFA from an NFA.

        The following code is 100% my own and took a while to figure
        out how to implement. This is still very much untested,
        so use at your own risk!
        """
        lambda_trans = self.lambda_trans()

        def reachable(state_set, start):
            state_set = set(state_set)
            # Initialize a set to keep track of visited
            # states to avoid lambda transition cycles.
            seen = set()
            state = start
            while state in lambda_trans:
                if state in seen:
                    break
                seen.add(state)
                state = lambda_trans[state]
                state_set.add(state)
            return state_set

        init = self.initial
        new_state = reachable({init}, init)  # type: ignore
        init = new_state
        visited = set()
        queue = deque()
        new_trans = {}
        first = True

        while first or queue:
            if first:
                queue.appendleft(new_state)
                first = False
            else:
                if (new_state := queue.pop()) in visited:
                    continue
            sym_map = {}
            for sym in self.alphabet:
                sym_state = set()
                for state in new_state:
                    trans = self.transfunc[state].get(sym)
                    if trans is None:
                        continue
                    if isinstance(trans, str):
                        trans = {trans}
                    reduce(ior, (reachable(trans, s) for s in trans), sym_state)  # type: ignore
                    for s in sym_state:
                        sym_state = reachable(sym_state, s)
                sym_map[sym] = sym_state
            new_state = frozenset(new_state)  # Make the new state hashable.
            new_trans[new_state] = sym_map
            queue.extendleft(new_trans[new_state][sym] for sym in self.alphabet)
            visited.add(new_state)
        ret = DFA(
            set(new_trans),
            self.alphabet.copy(),
            new_trans,
            init,
            {state for state in new_trans if state & self.accepting},
        )
        return ret

    to_dfa = powerset_construct

    @classmethod
    def union(cls, *dfas: DFA) -> DFA:
        ...  # To be implemented!

    def check(self, string: str) -> list[State]:
        return self.powerset_construct().check(string)


def main() -> None:
    nfas = [
        NFA(
            states={"q0", "q1", "q2", "q3"},
            alphabet={"0", "1"},
            transfunc={
                "q0": {"": "q2", "0": "q1"},
                "q1": {"1": {"q1", "q3"}},
                "q2": {"": "q1", "0": "q3"},
                "q3": {"0": "q2"},
            },
            initial="q0",
            accepting={"q2", "q3"},
        ),
        NFA(
            states={"q0", "q1", "q2", "q3"},
            alphabet={"a", "b"},
            transfunc={
                "q0": {"": "q1"},
                "q1": {"a": {"q1", "q2"}, "b": "q2"},
                "q2": {"a": {"q0", "q2"}, "b": "q3"},
                "q3": {"b": "q1"},
            },
            initial="q0",
            accepting={"q0"},
        ),
        NFA(
            states={"q0", "q1", "q2"},
            alphabet={"a", "b"},
            transfunc={
                "q0": {"": "q2", "b": "q1"},
                "q1": {"a": {"q1", "q2"}, "b": "q2"},
                "q2": {"a": "q0"},
            },
            initial="q0",
            accepting={"q0"},
        ),
    ]
    for nfa in nfas:
        dfa = nfa.to_dfa()
        pprint(dfa)


if __name__ == "__main__":
    main()
