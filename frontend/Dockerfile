
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
# The command is specified in docker-compose.yml
# CMD ["npm", "run", "dev"]
