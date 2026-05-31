FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

# Clean npm install
RUN npm ci || npm install

COPY . .

# Build next.js app
RUN npm run build

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["npm", "run", "start"]
