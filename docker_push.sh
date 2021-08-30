#!/bin/bash
docker-compose build scholar-utilities
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker tag axie-scholar-utilities epith/axie-scholar-utilities
docker push epith/axie-scholar-utilities
