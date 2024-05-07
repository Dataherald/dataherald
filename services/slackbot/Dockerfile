FROM node:18

LABEL Author="Juan Sebastián Valacco"
LABEL version="0.0.1"

WORKDIR /app

COPY package.json ./
COPY pnpm-lock.yaml ./

RUN npm install -g pnpm
RUN pnpm install

COPY . .

EXPOSE 3000

CMD [ "pnpm", "start" ]
