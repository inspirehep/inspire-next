#!/bin/bash -e

retry() {
    "$@" || "$@" || exit 2
}

TAG="inspirehep/inspire-next:latest"

echo "Building docker imagine"
retry docker build -t "$TAG" .

echo "Logging into Docker Hub"
retry docker login \
    "--username=$DOCKER_USERNAME" \
    "--password=$DOCKER_PASSWORD"

echo "Pushing image to ${TAG}"
retry docker push "${TAG}"

echo "Logging out"
retry docker logout
