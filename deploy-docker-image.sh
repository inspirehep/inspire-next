#!/bin/bash -e

TAG="${TRAVIS_TAG:-$(git describe --always --tags)}"

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

  echo "Building docker image"
  retry docker pull "${IMAGE}"
  retry docker build -t "${IMAGE}" -t "${IMAGE}:${TAG}" -f "${DOCKERFILE}" --build-arg FROM_TAG="${TAG}" --cache-from "${IMAGE}" .

  echo "Pushing image to ${IMAGE}:${TAG}"
  retry docker push "${IMAGE}:${TAG}"
  retry docker push "${IMAGE}"
}


logout() {
  echo "Logging out""${@}"
  retry docker logout
}

deploy() {
  environment=${1}
  image=${2}
  username='inspire-bot'
  token="${INSPIRE_BOT_TOKEN}"

  curl \
    -u "${username}:${token}" \
    -X POST \
    -H "Accept: application/vnd.github.v3+json" \
    -d '{"event_type":"deploy", "client_payload":{"environment":"'${environment}'", "image":"'${image}'", "tag":"'${TAG}'"}}' \
    https://api.github.com/repos/inspirehep/kubernetes/dispatches
}

main() {
  login
  buildPush "inspirehep/next"
  buildPush "inspirehep/next-assets" Dockerfile.with_assets
  buildPush "inspirehep/next-scrapyd" Dockerfile.scrapyd
  logout
  if [ -z "${TRAVIS_TAG}" ]; then
    deploy "qa" "inspirehep/next"
    deploy "qa" "inspirehep/next-assets"
    deploy "qa" "inspirehep/next-scrapyd"
  else
    deploy "prod" "inspirehep/next"
    deploy "prod" "inspirehep/next-assets"
    deploy "prod" "inspirehep/next-scrapyd"
  fi
}
main
