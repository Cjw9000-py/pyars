# pyars - A simple wrapper for argparse.
Packaging is managed with `pyproject.toml` (PEP 621). The only runtime dependency is [`attrs`](https://www.attrs.org/), installed automatically by `pip`.

## Installation

To install `pyars`, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/Cjw9000-py/pyars
```
2. Installation via pip
```bash
cd pyars
pip install .
```

To run the test suite, install dependencies from `requirements.txt` and execute `pytest`.

## Usage

`pyars` lets you declare command line interfaces using classes decorated with `@arguments`. Use `positional`, `option`, `flag`, and `command` to describe the CLI surface.

```python
from pathlib import Path
from pyars import arguments, positional, option, flag, command, Arguments

@arguments
class BuildArguments:
    targets: set[str] = positional(nargs='+', help='Targets to compile')
    root: Path = option('-r', convert=Path, default='.')
    verbose: bool = flag('-v', help='Enable verbose output')


@arguments
class ConsoleArguments:
    root: Path
    command: Arguments = command(build=BuildArguments)


if __name__ == '__main__':
    parsed_args = ConsoleArguments.parse_args()
    print(parsed_args)
```

* `positional` – declare positional parameters, supporting `nargs` and value conversion.
* `option` – add named options accepting values; `convert=` runs on CLI input and defaults before `choices` are validated, so define choices using the converted values. Short-only definitions still receive an automatic `--long-name` alias, and providing a `default` automatically sets `required=False`.
* `flag` – boolean toggles that default to `False` and become `True` when the flag is present. Short options automatically gain a `--long-name` alias derived from the attribute.
* `command` – nest other `@arguments` containers as sub-commands.

## Contributing

Install dependencies, including `attrs`, and run the test suite:
```bash
pip install -r requirements.txt
pytest
```

### Validation

Containers perform a validation pass before parsing. Sub-commands are required and validated recursively:

```python
ConsoleArguments.parse_args(['workspace'])  # raises SystemExit because no command is chosen
```
