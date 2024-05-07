# Contributing to Dataherald

Hi there! Thank you for even being interested in contributing. As a growing open source project we are open
to contributions, whether they be in the form of new features, integrations with other tools and frameworks, better documentation, or bug fixes.

## Guidelines

To contribute to this project, please follow a ["fork and pull request"](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) workflow.
Please do not try to push directly to this repo unless you are maintainer.

## Lint & Formatting

Maintaining code quality and adhering to coding standards are essential for a well-structured and maintainable codebase. Ruff Python Linter and Black code formatter are powerful tools that can help you achieve these goals. Should you experience any difficulty getting setup, please
contact a maintainer! Not only do we want to help get you unblocked, but we also want to make sure that the process is
smooth for future contributors.

In a similar vein, we do enforce certain linting, formatting, and documentation standards in the codebase.
If you are finding these difficult (or even just annoying) to work with, feel free to contact a maintainer for help -
we do not want these to get in the way of getting good code into the codebase.

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
