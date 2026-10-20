
# Stage 1 - Build application and Tailwind CSS
FROM node:20-alpine AS build-deps

WORKDIR /usr/src/app

COPY package.json package-lock.json ./
RUN npm install

COPY styles/ ./styles/
COPY coffee/ ./coffee/
# COPY .babelrc ./
COPY build.js ./

# Build application and Tailwind CSS
RUN npm run build

# Stage 2 - Serve static files with Nginx
FROM nginx:stable-alpine

WORKDIR /var/www/static

COPY static/css/ ./css/
COPY static/js/ ./js/
COPY static/fonts/ ./fonts/
COPY static/images/ ./images/
COPY static/*.* ./

COPY ./configs/nginx.nginx /etc/nginx/nginx.conf

COPY --from=build-deps /usr/src/app/build/ ./

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
