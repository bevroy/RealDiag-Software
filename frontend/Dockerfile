
FROM node:18-alpine AS builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ ./
RUN npm install && npm run build

FROM node:18-alpine
WORKDIR /app/frontend
COPY --from=builder /app/frontend /app/frontend
ENV NODE_ENV=production
EXPOSE 3000
CMD ["npm","run","start"]
