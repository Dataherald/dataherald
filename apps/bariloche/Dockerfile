FROM node:16

WORKDIR /app/programmatic-seo

# Install dependencies
COPY ./programmatic-seo /app/programmatic-seo
RUN npm install -g pnpm
RUN pnpm install

# Copy core code
#COPY . /app/

# Expose port 3000
EXPOSE 3000-3999

CMD pnpm run dev
