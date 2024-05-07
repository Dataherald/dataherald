FROM node:18-alpine

WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm i

COPY . .

# Next.js collects completely anonymous telemetry data about general usage. Learn more here: https://nextjs.org/telemetry
# Uncomment the following line to disable telemetry at run time
ENV NEXT_TELEMETRY_DISABLED 1

# Note: Don't expose ports here, Compose will handle that for us

# Start Next.js in development mode based on the preferred package manager
CMD pnpm dev