#!/bin/sh
envsubst '${VIRTUAL_HOST}' < /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/conf.d/nginx.conf
while :; do sleep 6h ; nginx -s reload; done & nginx -g "daemon off;"
exec "$@"
