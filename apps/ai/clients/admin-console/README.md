# Admin Console - Dataherald AI

The admin console is a front-end application for Data teams to access to their Dataherald AI (DH AI) resources. The main goal is to enable the Data teams to check and verify all the questions made to DH AI by the users within their organization. Also, the users of this application will be able to connect SQL databases and context stores.

## Technologies

- **Next.js**: The core framework of this project is Next.js, a React framework for server-rendered applications.
- **TypeScript**: TypeScript is used for static type checking in the project.
- **Tailwind CSS**: Tailwind CSS is a utility-first CSS framework for rapid UI development.
- **shadcn/ui**: This project uses the shadcn/ui component library, built on top of Radix UI and styled with Tailwind CSS, for the UI components.
- **Lucide React**: Lucide React is used for icons.
- **SWR**: SWR is a React Hooks library for data fetching.
- **ts-jest**: ts-jest is used for testing TypeScript code with Jest.

## Project Structure

The project follows the standard Next.js directory structure:

- `pages/`: Contains all page components.
- `components/`: Contains all reusable components.
- `lib/`: Contains utility functions.
- `styles/`: Contains global CSS styles.
- `next.config.js`: Next.js configuration file.
- `postcss.config.js`: PostCSS configuration file.
- `tailwind.config.js`: Tailwind CSS configuration file.
- `tsconfig.json`: TypeScript configuration file.

## Development

### Running the Project

1. Navigate into the project directory:

   ```
   cd project
   ```

2. Install dependencies:

   ```
   pnpm install
   ```

3. Run the development server:
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
