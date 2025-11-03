
FROM node:18-alpine
WORKDIR /app/frontend
COPY frontend /app/frontend
RUN npm install && npm run build || true
EXPOSE 3000
CMD ["npm","run","dev"]
