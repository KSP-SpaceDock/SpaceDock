# Stage 1 - the build process
FROM node:16 as build-deps
WORKDIR /usr/src/app
ADD package.json ./
ADD package-lock.json ./
RUN npm ci
ADD styles ./styles
ADD coffee ./coffee
ADD .babelrc ./
ADD build.js ./
RUN npm run build

# Stage 2 - the environment
FROM nginx:stable
WORKDIR /var/www/static
ADD static/css/ ./
ADD static/js/ ./
ADD static/fonts/ ./
ADD static/images/ ./
ADD static/*.* ./
ADD ./configs/nginx.nginx /etc/nginx/nginx.conf
COPY --from=build-deps /usr/src/app/build/ ./
