from pprint import pprint
from dfa import NFA


def main() -> None:
    nfas = [
        NFA(
            alphabet={"0", "1"},
            trans={
                1: {"": 3, "0": 2},
                2: {"1": {2, 4}},
                3: {"": 2, "0": 4},
                4: {"0": 3},
            },
            initial=1,
            accepting={3, 4},
        ),
        NFA(
            alphabet={"a", "b"},
            trans={
                "q0": {"": "q1"},
                "q1": {"a": {"q1", "q2"}, "b": "q2"},
                "q2": {"a": {"q0", "q2"}, "b": "q3"},
                "q3": {"b": "q1"},
            },
            initial="q0",
            accepting={"q0"},
        ),
        NFA(
            alphabet={"a", "b"},
            trans={
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
        print(dfa.states)
        pprint(dfa)


if __name__ == "__main__":
    main()
