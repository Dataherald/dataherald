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
