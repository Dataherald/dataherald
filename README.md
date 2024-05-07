# dataherald monorepo

<p align="center">
  <a href="https://dataherald.com"><img src="https://files.dataherald.com/logos/dataherald.png" alt="Dataherald logo"></a>
</p>

<p align="center">
    <b>Query your structured data in natural language</b>. <br />
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

Dataherald is a natural language-to-SQL engine built for enterprise-level question answering over structured data. It allows you to set up an API from your database that can answer questions in plain English. You can use Dataherald to:

- Allow business users to get insights from the data warehouse without going through a data analyst
- Enable Q+A from your production DBs inside your SaaS application
- Create a ChatGPT plug-in from your proprietary data

This repository hosts four natural language-to-SQL components under `/services`:

1. engine: The core component for natural language-to-SQL. If you would like to use the dataherald API only, then you will not need to run other componenets.
2. enterprise: The enterprise component of dataherald. It adds authentication, organizations and users, and other business log to dataherald. Requires engine to run.
3. admin-console: The front-end component of dataherald, you will need to run both engine and enterprise and point the backend to enterprise in order for admin-console to work.
4. slack: A slackbot which allows users from a slack channel to interact with dataherald. Requires both engine and enterprise to run.

For more information on each component, please take a look at their `README.md` files.

## Contributing
As an open-source project in a rapidly developing field, we are open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see [here](CONTRIBUTING.md).