# PATCHED (audit fix): no USER instruction previously, so the container
# ran as root. Switched to the `node` user that the official node:20-alpine (Next.js 16 needs Node >= 20.9)
# image already ships with, after fixing ownership of the app directory.

FROM node:20-alpine AS builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
COPY frontend/ ./
RUN npm install && npm run build

FROM node:20-alpine
WORKDIR /app/frontend
COPY --from=builder /app/frontend /app/frontend
ENV NODE_ENV=production
EXPOSE 3000
COPY frontend/docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh
# Ensure curl is available for the container healthcheck and runtime probes
# Alpine images don't include curl by default.
RUN apk add --no-cache curl

# PATCHED: run as the non-root `node` user (built into node:20-alpine)
# instead of root.
RUN chown -R node:node /app/frontend
USER node

ENTRYPOINT ["./docker-entrypoint.sh"]
