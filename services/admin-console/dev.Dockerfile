FROM node:18-alpine

LABEL Author="Juan Sebastian Valacco"

WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm i

COPY . .

# Next.js collects completely anonymous telemetry data about general usage. Learn more here: https://nextjs.org/telemetry
# Uncomment the following line to disable telemetry at run time
ENV NEXT_TELEMETRY_DISABLED 1

# Docker network URL for the API -- used for nextjs server side API calls inside the docker network
# The browser needs to access the API from the exposed port in the docker host (i.e.: localhost:3001)
ENV DOCKER_API_URL='http://api:3001' 

# Note: Don't expose ports here, Compose will handle that for us

# Start Next.js in development mode based on the preferred package manager
CMD pnpm dev