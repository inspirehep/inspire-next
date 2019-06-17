#!/bin/bash -e
IMAGE="inspirehep/inspire-next"

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
  GIT_DESC="$(git describe --always || echo)"

  echo "Building docker image"
  retry docker build -t "${IMAGE}:${TAG}" -f "${DOCKERFILE}" .
  
  echo "Pushing image to ${IMAGE}:${TAG}"
  retry docker push "${IMAGE}:${TAG}"

  if  [ -n ${GIT_DESC+x} ]
  then
    if [ "${TAG}" == "latest" ]
    then
      FULL_TAG="${IMAGE}:${GIT_DESC}"
    else
      FULL_TAG="${IMAGE}:${GIT_DESC}-${TAG}"
    fi
    echo "Pushing image to ${FULL_TAG}"
    docker tag "${IMAGE}:${TAG}" "${FULL_TAG}"
    retry docker push "${FULL_TAG}"
  fi
}


logout() {
  echo "Logging out""${@}"
  retry docker logout
}


main() {
  login
  buildPush "latest"
  buildPush "assets" Dockerfile.with_assets
  buildPush "scrapyd" Dockerfile.scrapyd
  logout
}
main
