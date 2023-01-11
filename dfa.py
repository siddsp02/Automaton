"""NFA and DFA Library.

References:
    - https://en.wikipedia.org/wiki/Powerset_construction#CITEREFHopcroftUllman1979
    - https://www.youtube.com/watch?v=jMxuL4Xzi_A&ab_channel=EasyTheory
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import filterfalse
from typing import Generic, KeysView, TypeVar

T = TypeVar("T")
LAMBDA = ""  # Represents lambda transition in an NFA.


@dataclass
class DFA(Generic[T]):
    alphabet: set[str]
    trans: dict[T, dict[str, T]]
    initial: T
    accepting: set[T]

    @property
    def states(self) -> KeysView[T]:
        return self.trans.keys()

    def check(self, string: str) -> list[T]:
        curr = self.initial
        path = [curr]
        for char in string:
            path.append(curr := self.trans[curr][char])
        return [] if path[-1] not in self.accepting else path

    def to_regex(self) -> str:
        ...  # To be implemented.


class NFA(DFA[T]):
    def lambda_trans(self) -> dict[T, T]:
        """Returns all lambda transitions in the form of state pairs."""
        lambda_trans = {}
        for state, edges in self.trans.items():
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
                    trans = self.trans[k].get(sym)
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
        return DFA(
            self.alphabet.copy(),
            new_trans,
            init,
            {state for state in new_trans if state & self.accepting},
        )

    to_dfa = powerset_construct

    @classmethod
    def union(cls, *dfas: DFA[T]) -> DFA[T]:
        ...  # To be implemented.

    def check(self, string: str) -> list[T]:
        return self.powerset_construct().check(string)


def main() -> None:
    ...


if __name__ == "__main__":
    main()
