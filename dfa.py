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
from typing import Generic, TypeVar


T = TypeVar("T")
LAMBDA = ""  # Represents lambda transition in an NFA.


class Language:
    ...


@dataclass
class DFA(Generic[T]):
    states: set[T]
    alphabet: set[str]
    transfunc: dict[T, dict[str, T]]
    initial: T
    accepting: set[T]

    def check(self, string: str) -> list[T]:
        curr = self.initial
        path = [curr]
        for char in string:
            path.append(curr := self.transfunc[curr][char])
        return [] if path[-1] not in self.accepting else path

    def to_regex(self) -> str:
        ...  # To be implemented.


class NFA(DFA):
    def lambda_trans(self) -> dict[T, T]:
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

        def reachable(states):
            ret = set(states)
            for state in states:
                # Initialize a set to keep track of visited
                # states to avoid lambda transition cycles.
                seen = set()
                while state in lambda_trans:
                    if state in seen:
                        break
                    seen.add(state)
                    state = lambda_trans[state]
                    ret.add(state)
            return ret

        new_state = reachable({self.initial})  # type: ignore
        init = new_state
        queue = deque([init])
        visited = set()
        new_trans = {}
        first = True
        while queue:
            if first:
                first = False
            elif (new_state := queue.pop()) in visited:
                continue
            sym_map = {}
            for sym in self.alphabet:
                sym_state = set()
                for k in new_state:
                    trans = self.transfunc[k].get(sym)
                    if trans is None:
                        continue
                    if not isinstance(trans, set):
                        trans = {trans}
                    for state in (trans, sym_state):
                        sym_state |= reachable(state)
                sym_map[sym] = set(sym_state)
            new_state = frozenset(new_state)  # Make the new state hashable.
            new_trans[new_state] = sym_map
            queue.extendleft(map(new_trans[new_state].get, self.alphabet))
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
        ...  # To be implemented.

    def check(self, string: str) -> list[T]:  # type: ignore
        return self.powerset_construct().check(string)


def main() -> None:
    nfas = [
        NFA(
            states={1, 2, 3, 4},
            alphabet={"0", "1"},
            transfunc={
                1: {"": 3, "0": 2},
                2: {"1": {2, 4}},
                3: {"": 2, "0": 4},
                4: {"0": 3},
            },
            initial=1,
            accepting={3, 4},
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
