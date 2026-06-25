
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
COPY frontend/docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh
# Ensure curl is available for the container healthcheck and runtime probes
# Alpine images don't include curl by default.
RUN apk add --no-cache curl

ENTRYPOINT ["./docker-entrypoint.sh"]
