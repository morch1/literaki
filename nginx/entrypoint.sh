#!/bin/sh
envsubst '${NGINX_DOMAIN}' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/nginx.conf
while :; do sleep 6h ; nginx -s reload; done & nginx -g "daemon off;"
exec "$@"
