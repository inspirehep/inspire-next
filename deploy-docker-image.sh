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
  TAG="$(git describe --always)"


  echo "Building docker image"
  retry docker build -t "${IMAGE}" -t "${IMAGE}:${TAG}" -f "${DOCKERFILE}" .

  echo "Pushing image to ${IMAGE}:${TAG}"
  retry docker push "${IMAGE}:${TAG}"
  retry docker push "${IMAGE}"

  echo "Deploying to QA"
  deployQA ${IMAGE} ${TAG}
}


logout() {
  echo "Logging out""${@}"
  retry docker logout
}

deployQA() {
  IMAGE="${1}"
  TAG="${2}"

  curl -X POST \
    -F token=${DEPLOY_QA_TOKEN} \
    -F ref=master \
    -F variables[IMAGE_NAME]=${IMAGE} \
    -F variables[NEW_TAG]=${TAG} \
    https://gitlab.cern.ch/api/v4/projects/62928/trigger/pipeline
 }


main() {
  login
  buildPush "inspirehep/next"
  buildPush "inspirehep/next-assets" Dockerfile.with_assets
  buildPush "inspirehep/next-scrapyd" Dockerfile.scrapyd
  logout
}
main
