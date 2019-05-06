#!/bin/bash -e

retry() {
    "${@}" || "${@}" || exit 2
}


login() {
  echo "Logging into Docker Hub"
  retry docker login \
      "--username=${DOCKER_USERNAME}" \
      "--password=${DOCKER_PASSWORD}"
}


buildPush() {
  TAG="${1}"
  DOCKERFILE="${2:-Dockerfile}"
  echo "Building docker imagine"
  retry docker build -t "${TAG}" -f "${DOCKERFILE}" .
  
  echo "Pushing image to ${TAG}"
  retry docker push "${TAG}"
}


logout() {
  echo "Logging out""${@}"
  retry docker logout
}


main() {
  login
  buildPush "inspirehep/inspire-next:latest"
  buildPush "inspirehep/inspire-next:assets" Dockerfile.with_assets
  logout
}
main
