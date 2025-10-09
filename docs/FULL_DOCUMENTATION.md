# pyars Documentation

pyars relies on the [`attrs`](https://www.attrs.org/) package. It is installed automatically when you install pyars.

`pyars` is a lightweight wrapper around `argparse` that lets you declare command
line interfaces using `attrs` classes. Fields are annotated with special
argument descriptors which control how each attribute is parsed.

## Defining Arguments

Decorate your class with `@arguments` to enable parsing:

```python
from pathlib import Path
from pyars import arguments, positional, option, flag, command

@arguments
class BuildArgs:
    targets: set[str] = positional(nargs='+', help='Targets to build')
    root: Path = option('-r', convert=Path, default='.')
    verbose: bool = flag('-v', help='Enable verbose output')
```

Running `BuildArgs.parse_args()` returns an instance populated from
``sys.argv``.

## Argument Types

* **positional** – declare positional parameters. `nargs` and `convert` let you customise arity and type conversion.
* **option** – named options that expect a value. Values pass through the option's `convert` callable before validation, so `choices` should contain the converted representation (for example, `Path` instances rather than strings). When no names are supplied a `--long-name` is generated automatically; supplying only short names still gains a long alias. Providing a `default` marks the option as optional (`required=False`) even when not specified explicitly.
* **flag** – boolean toggles that default to ``False`` and become ``True`` when present.
* **command** – selects a sub-command implemented by another argument
  container.

Refer to `example.py` or `new-spec.py` for a full usage example.

### Automatic Long Alias Example

Supplying only a short option name still provides a derived long alias:

```python
@arguments
class ServeArgs:
    port: int = option('-p', convert=int, help='Port to bind')

ServeArgs.parse_args(['--port', '8080'])
```

On the command line this enables either form:

```bash
python app.py -p 8080
python app.py --port 8080
```

## Advanced Usage

`ArgumentContainer.new_parser()` can be customised further by supplying
additional `ArgumentParser` options or a callback. Extra positional or keyword
arguments are forwarded directly to `ArgumentParser` while callbacks receive the
fully configured parser for modification:

```python
def with_debug(parser: ArgumentParser) -> None:
    parser.add_argument('--debug', action='store_true')

parser = BuildArgs.new_parser(
    callbacks=with_debug,
    description='Build projects',
)
args = parser.parse_args(['proj', '--debug'])
```

The callback gets access to the parser instance so any additional options or
settings remain active when parsing command lines.

## Validation

Containers perform a validation pass before parsing. Choosing a sub-command is
mandatory and nested commands are validated recursively.

```python
ConsoleArgs.parse_args(['proj'])  # SystemExit: the command is required
```

