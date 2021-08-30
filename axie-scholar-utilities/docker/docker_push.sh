#!/bin/bash/env bash
set -e # Halt script on error
echo "Building image"
docker-compose build scholar-utilities
echo "Logging in to DockerHub"
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
echo "Tagging image"
docker tag axie-scholar-utilities epith/axie-scholar-utilities
echo "Pushing image to DockerHub"
docker push epith/axie-scholar-utilities
