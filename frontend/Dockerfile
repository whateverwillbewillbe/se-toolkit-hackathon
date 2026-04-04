# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_DEFAULT_USER_ID=1
ENV VITE_DEFAULT_USER_ID=${VITE_DEFAULT_USER_ID}

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
