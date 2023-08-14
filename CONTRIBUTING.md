



## Lint & Formatting

Maintaining code quality and adhering to coding standards are essential for a well-structured and maintainable codebase. Ruff Python Linter and Black code formatter are powerful tools that can help you achieve these goals.

### Ruff Python Linter

[Ruff Python Linter](https://beta.ruff.rs/docs/) analyzes Python code for errors, enforces coding standards, and provides suggestions for improvement.

The [rules](https://beta.ruff.rs/docs/rules/) are set in the [pyproject.toml](./pyproject.toml) file.

Lint all files in the current directory:

```shell
ruff check .
```

Lint and fix whenever possible:
```shell
ruff check --fix .
```

Lint specific files:

```shell
ruff check path/to/code.py
```

### Black Code Formatter

[Black](https://black.readthedocs.io/en/stable/#) is a Python code formatter that ensures consistent code style and improves readability.

Format all files in the current directory:

```shell
black .
```

Format a specific file:

```shell
black path/to/code.py
```

> Recommendation: Look up for Ruff and Black IDE extensions to easily format and lint the code automatically while you're developing.


## Testing with Docker
Once your containers are running just execute the next command
```
docker-compose exec app pytest
```
