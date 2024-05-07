<<<<<<< HEAD
<<<<<<< HEAD
# Dataherald Monorepo

Welcome to the Dataherald Monorepo. This repository hosts all of our company's applications located in the `/apps` directory. Each application has its own dedicated folder and specific pipeline for building and deployment.

## Structure

The `/apps` directory hosts all the individual applications. Each application has its own directory and should contain its own README file with specific instructions about how to use, build and deploy.

Structure example:

```bash
.
└── apps
    ├── app1
    ├── app2
    ├── app3
    └── ...
└── libs
    ├── lib1
    ├── lib2
    ├── lib3
    └── ...
```

## Continuous Integration/Continuous Delivery

Our CI/CD pipelines are handled through GitHub Actions. These workflows build Docker images of the applications and deploy them to AWS or Vercel depending on the specific application requirements.

GitHub Actions have been configured to optimise the build process. Each action will only be triggered if there are changes in the relevant directories. This ensures that we are only running actions when necessary, saving on build time and resources.

## Git Workflow

Our Git workflow consists of working on the `main` branch. Any merge to `main` triggers a deployment to our staging environments.

Release is done through git tags. When a new tag is created, it triggers the pipeline for production deployment.

### Local Development

When developing locally, the strategy is to `rebase` from `main` to keep your feature branch up to date. After your feature has been developed and tested, you can open a Pull Request against the `main` branch. Merge to `main` can be done with a merge commit.
=======
# dataherald
=======
# Dataherald Monorepo
>>>>>>> e45f91c1 (DH-5770 engine cleanup)

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

This respository hosts 4 projects total: 

1. Admin Console: The front-end component for dataherald. It requires Enterprise and Engine both to be running in order to work.

2. Engine: The core component for language-to-SQL engine. If you just want to use the language-to-SQL API, then only the Engine is needed.

3. Enterprise: A wrapper for the Engine component with business logic. It adds authentication, organizations, users, usage based payment, and other logic on top of the Engine. It requires Engine to be running in order to work

3. Slackbot: A slack bot that allows interactions to the language-to-SQL engine via Slack channel messages. It requires Enterprise and Engine both to be running in order to work.

Each project is deployable via docker image. If you want to connect different projects together, you will need to setup the environment variables with the project url.

For more details about each individual project, please check the their `README.md` files for more information.

## Contributing
As an open-source project in a rapidly developing field, we are open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see [here](CONTRIBUTING.md).