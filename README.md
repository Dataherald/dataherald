# Dataherald monorepo

<p align="center">
  <a href="https://dataherald.com"><img src="https://files.dataherald.com/logos/dataherald.png" alt="Dataherald logo"></a>
</p>

<p align="center">
    <b>Query your relational data in natural language</b>. <br />
</p>

<p align="center">
  <a href="https://discord.gg/A59Uxyy2k9" target="_blank">
      <img src="https://img.shields.io/discord/1138593282184716441" alt="Discord">
  </a> |
  <a href="./LICENSE" target="_blank">
      <img src="https://img.shields.io/static/v1?label=license&message=Apache 2.0&color=white" alt="License">
  </a> |
  <a href="https://dataherald.readthedocs.io/" target="_blank">
      Docs
  </a> |
  <a href="https://www.dataherald.com/" target="_blank">
      Homepage
  </a>
</p>

Dataherald is a natural language-to-SQL engine built for enterprise-level question answering over relational data. It allows you to set up an API from your database that can answer questions in plain English. You can use Dataherald to:

- Allow business users to get insights from the data warehouse without going through a data analyst
- Enable Q+A from your production DBs inside your SaaS application
- Create a ChatGPT plug-in from your proprietary data

This repository contains four components under `/services` which can be used together to set up an end-to-end Dataherald deployment:

1. Engine: The core natural language-to-SQL engine. If you would like to use the dataherald API without users or authentication, running the engine will suffice.
2. Enterprise: The application API layer which adds authentication, organizations and users, and other business logic to Dataherald. 
3. Admin-console: The front-end component of Dataherald which allows a GUI for configuration and observability. You will need to run both engine and enterprise for the admin-console to work.
4. Slackbot: A slackbot which allows users from a slack channel to interact with dataherald. Requires both engine and enterprise to run.

For more information on each component, please take a look at their `README.md` files.

## Running locally

Each component in the `/services` directory has its own `docker-compose.yml` file. To set up the environment, follow these steps:

1. **Set Environment Variables**:
   Each service requires specific environment variables. Refer to the `.env.example` file in each service directory and create a `.env` file with the necessary values. 
   > For the Next.js front-end app is `.env.local`
2. **Run Services**:
   You can run all the services using a single script located in the root directory. This script creates a common Docker network and runs each service in detached mode.

Run the script to start all services:

```bash
sh docker-run.sh
```

## Contributing
As an open-source project in a rapidly developing field, we are open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see [here](CONTRIBUTING.md).
