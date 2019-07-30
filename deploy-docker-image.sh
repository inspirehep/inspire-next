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
  IMAGE="${1}"
  DOCKERFILE="${2:-Dockerfile}"
  GIT_DESC="$(git describe --always)"

  echo "Building docker image"
  retry docker build -t "${IMAGE}" -t "${IMAGE}:${GIT_DESC}" -f "${DOCKERFILE}" .
  
  echo "Pushing image to ${IMAGE}:${TAG}"
  retry docker push "${IMAGE}:${TAG}"
  retry docker push "${IMAGE}"
}


logout() {
  echo "Logging out""${@}"
  retry docker logout
}


main() {
  login
  buildPush "inspirehep/next"
  buildPush "inspirehep/next-assets" Dockerfile.with_assets
  buildPush "inspirehep/next-scrapyd" Dockerfile.scrapyd
  logout
}
main
