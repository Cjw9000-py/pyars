# pyars Documentation

`pyars` is a lightweight wrapper around `argparse` that lets you declare command
line interfaces using `attrs` classes. Fields are annotated with special
argument descriptors which control how each attribute is parsed.

## Defining Arguments

Decorate your class with `@arguments` to enable parsing:

```python
from pyars import arguments, positional, flag, switch, command

@arguments
class BuildArgs:
    projects: set[str] = positional(nargs='+', help='Projects to build')
    root: Path = flag(default='cwd')
    verbose: bool = switch(help_suffix='verbose output')
```

Running `BuildArgs.parse_args()` returns an instance populated from
``sys.argv``.

## Argument Types

* **positional** – creates a mandatory positional argument.
* **flag** – standard option that accepts a value and may have defaults.
* **switch** – boolean flag supporting ``--feature`` / ``--no-feature``.
* **command** – selects a sub-command implemented by another argument
  container.

Refer to `example.py` for a full usage example.

## Validation

Containers perform a validation pass before parsing. Using mutually
exclusive switches results in ``InvalidArgumentsError``:

```python
BuildArgs.parse_args(['proj', '--verbose', '--no-verbose'])
```

