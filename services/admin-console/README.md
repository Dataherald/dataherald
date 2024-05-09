# Admin Console - Dataherald

The admin console is a front-end application for users to access to their Dataherald resources. The users of this application will be able to connect SQL databases, test the platform through a Playground, see the query generations and verify them in order to increase the platform training dataset by adding golden SQL pairs.

## Technologies

- **Next.js**: The core framework of this project is Next.js, a React framework for server-rendered applications.
- **TypeScript**: TypeScript is used for static type checking in the project.
- **Tailwind CSS**: Tailwind CSS is a utility-first CSS framework for rapid UI development.
- **shadcn/ui**: This project uses the shadcn/ui component library, built on top of Radix UI and styled with Tailwind CSS, for the UI components.
- **Lucide React**: Lucide React is used for icons.
- **SWR**: SWR is a React Hooks library for data fetching.
- **ts-jest**: ts-jest is used for testing TypeScript code with Jest.

## Project Structure

The project follows the standard Next.js directory structure inside `src/`:

- `components/`: reusable components
- `constants/`: relevant constants in the code
- `contexts/`: React contexts
- `hooks/`: React custom hooks such as the API call hooks and more
- `lib/`: utility functions.
- `models/`: types and interfaces 
- `pages/`: route pages
- `styles/`: global CSS styles
- `config.ts`: environment variables resolver
- `next.config.js`: Next.js configuration file
- `postcss.config.js`: PostCSS configuration file
- `tailwind.config.js`: Tailwind CSS configuration file
- `tsconfig.json`: TypeScript configuration file

## Development

### Running the Project

1. Navigate into the project directory:
2. **Prepare your `.env.local` file** with the necessary environment variables specific to your local setup.
3. Install dependencies:

   ```
   pnpm install
   ```

4. Run the development server:
   ```
   pnpm dev
   ```

The project will be available at `http://localhost:3000`.

### Linting and Testing

You can lint your code using ESLint and test it with Jest using the following commands:

- **Linting**:

  ```
  pnpm lint
  ```

- **Testing**:
  ```
  pnpm test
  ```

## Running the App Locally with Docker Compose

For a consistent development environment, use Docker:

1. **Prepare your `.env.local` file** with the necessary environment variables specific to your local setup.

2. **Start the app using Docker Compose:**
   Launch your app with all its services using:
   ```bash
   docker-compose up --build
   ```
   This approach uses the `dev.Dockerfile`, and you can access the app at `http://localhost:3000`.

## Deploy

### Setting Up an Auth0 Application

The project uses `nextjs-auth0` sdk to connect with Auth0 provider. Here is a [quick guide](https://auth0.com/docs/quickstart/webapp/nextjs/01-login). Most of those steps are already setup in the project.

To integrate Auth0 authentication:

1. **Register your application on Auth0.** Go to the Auth0 dashboard and create a new application.

2. **Configure URLs:**
   Set these URLs in your Auth0 application settings:
   - **Callback URL:** This should match the URL path that handles the Auth0 response (e.g., `http://localhost:3000/api/auth/callback`).
   - **Logout URL:** The URL that triggers user logout (e.g., `http://localhost:3000/`).

3. **Set environment variables in your deployment:**
   Use the variables you configured in Auth0 in your production or development environment.


### Docker

Deploy your app in a production environment with these steps:

1. **Environment Variables:**
   Properly configure a `.env.production` file setting up all the required environment variables similar to local environments but accordign to your production config.

   >Ensure these values are securely managed and not exposed in your source code.

2. **Build the Docker image for production using `prod.Dockerfile`:**
   Create a Docker image optimized for production using:
   ```bash
   docker build -f prod.Dockerfile -t admin-console .
   ```

3. **Run the container:**
   Launch your production app:
   ```bash
   docker run -p 80:3000 admin-console
   ```

> Next.js version of this project bundles all the environment variables into the generated code from `next build`. The Docker image is the one that runs this command and generates the nextjs app that will run. Therefore, all the environment variables need to be setup to the nextjs project when building the Docker image.  
[NextJS env vars docs](https://nextjs.org/docs/pages/building-your-application/configuring/environment-variables) -- [NextJS docker deploy](https://nextjs.org/docs/pages/building-your-application/deploying#docker-image)

>Follow your cloud provider recommendations on how to push and deploy the docker image of the app

## Additional Documentation

- **Dependency Management:** Use `pnpm` for all dependency management tasks to ensure consistent installations across environments.
- **Script Usage:** Utilize the predefined scripts in `package.json` for routine tasks:
  - `pnpm run dev` for local development.
  - `pnpm run build` to prepare a production build.
  - `pnpm run test` for running unit tests.
- **Troubleshooting:** If you encounter issues with Auth0, verify the environment variables and configurations as per the steps above. For other common problems, ensure your dependencies are up-to-date and check for any errors in the console.
