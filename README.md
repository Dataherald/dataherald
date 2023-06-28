# dataherald

Dataherald is a text-to-sql engine built for enteprise-level question answering over structured data. It allows you to set up an API from your database that can answer questions in plain English. You can use Dataherald to:

- Enable Q+A from your production DBs inside your SaaS application
- Allow business users to get insights from the data warehouse without going through a data analyst
- Create a ChatGPT plug-in from your proprietary data

... and many more!

Documentation

Discord

## Overview

### Background

LLMs are a phenomenal piece of technology, and the latest models have gotten very good at writing SQL. However we could not get existing frameworks to work with our structured data at a level which we could incorporate into our application. That is why we built and released this engine.

### Goals

Dataherald is built to:

- Be easy to set up and add context
- Be able to answer complex queries
- Get better with usage
- Be fast

## Get Started

The simplest way to set up Dataherald is to use to create a managed deployment with a hosted API. We are rolling this service to select customers. Sign up for the waitlist <link>.

You can also self-host the engine locally.

## Run Dataherald locally

To run Dataherald locally simply run

uvicorn dataherald.app:app

## Develop

Things to know when developing for dataherald package.

### Lint & Formatting

Maintaining code quality and adhering to coding standards are essential for a well-structured and maintainable codebase. Ruff Python Linter and Black code formatter are powerful tools that can help you achieve these goals.

#### Ruff Python Linter

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

#### Black Code Formatter

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


## Running with Docker

## Prerequisites
* If you use a MAC computer you should have installed docker for MAC, check [here](https://docs.docker.com/desktop/install/mac-install/)

## Steps to setup and run docker app 
1. Create `.env` file, you can use the `.env.example` variables and fill them up
```
cp dataherald/.env.example dataherald/.env
```
2. Build docker images, create containers and raise them (Check that Docker service is running). It should raise the app and mongo container
```
docker-compose up
```
