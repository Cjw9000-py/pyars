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

You can also check the `example.py` in the root of the project.
The usage is straightforward.

```python
from pathlib import Path
from pyars import arguments, positional, flag, switch, command, Arguments

@arguments
class BuildArguments:
    projects: set[str] = positional(nargs='+', help="The projects you want to use")
    root: Path = flag(extra_opts='--root-path', default='cwd', help="The root dir to use")
    verbose: bool = switch(help_suffix="verbose output")
    parallel: int = flag(nargs='?', type=int, default=1, help="Number of concurrent tasks to run")
    colorize_output: bool = switch(name='colorize', help_suffix="colorized console output")


if __name__ == "__main__":
    parsed_args = BuildArguments.parse_args()
    print(parsed_args)

```

## Contributing

Install dependencies, including `attrs`, and run the test suite:
```bash
pip install -r requirements.txt
pytest
```

### Validation

Providing conflicting switches raises an ``InvalidArgumentsError``:

```python
BuildArguments.parse_args(['proj', '--verbose', '--no-verbose'])
```
