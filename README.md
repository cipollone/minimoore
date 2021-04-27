# Minimoore
Minimoore is a small implementation of finite state transducers.
Currently, only the Moore machine is implemented, but we'll add other features.

## Install
This package can be installed as usual with pip:

    pip install https://github.com/cipollone/minimoore

Or, we can install a specific version with tested dependencies, by cloning the repository and running:

    poetry install --no-dev

From the project directory. Omit the `--no-dev` option if you're installing for local development.

Then, `import minimoore` in your project.

## Use

A transducer can be instantiated with methods of the specific transducer class, or via a builder. This is the syntax of the builder for Moore machines:

    builder = MooreBuilder[int, str]()
    (builder.state("s0").init().output("a").to(0, "s1").to(1, "s0"))
    (builder.state("s1").output("a").to(0, "any-name").to(1, "s1"))
    (builder.state("any-name").output("b").to(0, "s0").to(1, "s0"))

We can now get `builder.machine`, use it or save it to a Dot file. Moore machines can be minimized, completed (more to add later).
