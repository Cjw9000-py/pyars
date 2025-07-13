# pyars - a simple wrapper for argparse.

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

## Usage

You can also check the `example.py` in the root of the project.
The usage is straightforward.

```python
from pyars import *

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
