"""Minimize a table of transitions.

This scripts reads an experience of transitions with the following format:
    data["s"] : an array of states of shape (n_samples, state_size)
    data["a"] : an array of actions of shape (n_samples,)
    data["s'"] : states reached after each (s, a)
    data["q"] : an array of q values of shape (n_samples, n_actions)

This script builds a moore machine using as output the optimal action
in each state. This moore machine is then minimized.
"""

import argparse
import pickle

import numpy as np

from minimoore.moore import MooreBuilder


def main():
    """Run"""

    # Simple argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("pickle", type=str, help="A pickle file (see docstring)")
    parser.add_argument("--save", type=str, help="Save output to this path")
    args = parser.parse_args()

    # Load file
    with open(args.pickle, "rb") as f:
        data = pickle.load(f)

    # Parse data
    states, actions, nexts, qtable = data["s"], data["a"], data["s'"], data["q"]

    # Compute set of states, and optimal actions
    optimal_actions = {
        askey(states[i, :]): np.argmax(qtable[i, :])
        for i in range(states.shape[0])
    }

    # Create a machine with these transitions
    builder = MooreBuilder()
    for i in range(states.shape[0]):
        s, a, sp = states[i], actions[i], nexts[i]

        (builder.state(askey(s))
            .output(optimal_actions[askey(s)])
            .to(a, askey(sp)))

    # NOTE: what initial state makes sense here?
    first = askey(states[0, :])
    builder.state(first).init()

    # Complete with missing outputs and transitions
    machine = builder.machine
    machine.complete_outputs("_")
    machine.complete_sink("_")

    # Minimize
    minimized = machine.minimize()

    # Save graph
    minimized.save_graphviz(args.save)

    # Log
    print(f"Original Moore machine have {machine.n_states}")
    print(f"Minimized Moore machine has {minimized.n_states}")


def askey(array):
    """Convert numpy array to hashable type."""
    return array.tobytes()


if __name__ == "__main__":
    main()
