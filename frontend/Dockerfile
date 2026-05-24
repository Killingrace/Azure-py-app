# Stage 1: Build the React application
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# You can pass VITE_API_URL via --build-arg if building specifically for an environment
# But usually relative paths or dynamic runtime configs are preferred.
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
# Copy built assets from the 'build' stage
COPY --from=build /app/dist /usr/share/nginx/html
# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Port 80 is exposed by default in nginx:alpine, but making it explicit
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
