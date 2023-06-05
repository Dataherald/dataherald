# ChatDH

A front-end OpenAI + Dataherald visualizations chat using Next.js, TypeScript, and Tailwind CSS.

## Running Locally

**1. Install Dependencies**

```bash
pnpm install
```

**2. Setup environment variables**

To be able to start the project, you can follow the next steps:

1. Remove the `.example` part of the name from the [env local file example](./.env.local.example)
2. Fill the empty secrets fields with the content from the `development` env variables of the project. You can find them [here](https://vercel.com/dataherald/chat-dh/settings/environment-variables). If you don't have access. Request help from Amir or Valak.

> Note that the `.env.local` is personal and won't be pushed to the shared codebase.

**3. Run App**

```bash
pnpm dev
```

## Authentication

Authentication is handled by our Auth0 client and implemented in this project using their official [NextJS SDK](https://github.com/auth0/nextjs-auth0)

## Code Format

Prettier is added to the projects and a check is run on the PRs to check the correct format. To fix any format issue you can run `pnpm run format`
